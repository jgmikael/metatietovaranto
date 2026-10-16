"""Real pySHACL and PostgreSQL workflow checks; synthetic RDF only."""
from pathlib import Path
from uuid import UUID
import pytest
from rdflib import Graph
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from apps.api.main import engine, app
from apps.api.models import Draft
from apps.api.semantic_validation import POLICY
from helpers import body, create, change, import_profile, profile_input, publish, ORG

EXAMPLE = Path('fixtures/semantic-example-demo.ttl').read_text()


def with_example(content, serialization='turtle'):
    return {'content': content, 'serialization': serialization, 'synthetic': True}


def submit(client, draft):
    return client.post(f"/api/v1/drafts/{draft['draftId']}/submit", headers={'If-Match': draft['etag']})


@pytest.mark.parametrize('content,rule', [
    ('@prefix d:<https://example.org/metatietovaranto/demo/>. <urn:demo> a d:Company.', 'MinCountConstraintComponent'),
    (EXAMPLE.replace('"Synteettinen Esimerkki Oy"', '123'), 'DatatypeConstraintComponent'),
    (EXAMPLE.replace('"Synteettinen Esimerkki Oy"', '"Yksi", "Kaksi"'), 'MaxCountConstraintComponent'),
    ('<urn:unrelated> <urn:name> "Ei kohdetta".', 'EXAMPLE_TARGET_REQUIRED'),
])
def test_invalid_example_blocks_review_with_rule_and_path(client, content, rule):
    profile = import_profile(client)
    draft = create(client, body() | {'profileSnapshotId': profile['id'], 'syntheticExample': with_example(content)})
    report = draft['semanticValidation']
    assert report['status'] == 'invalid'
    assert any(item['ruleId'].endswith(rule) and item['path'] == '/syntheticExample' for item in report['results'])
    assert submit(client, draft).status_code == 422
    assert client.get('/api/v1/products').json()['total'] == 0


@pytest.mark.parametrize('serialization,fmt', [('turtle','turtle'), ('rdfxml','xml'), ('jsonld','json-ld')])
def test_valid_examples_in_three_rdf_formats(client, serialization, fmt):
    profile = import_profile(client)
    content = Graph().parse(data=EXAMPLE, format='turtle').serialize(format=fmt)
    draft = create(client, body() | {'profileSnapshotId': profile['id'], 'syntheticExample': with_example(content, serialization)})
    report = draft['semanticValidation']
    assert report['status'] == 'conforms' and report['profileConforms'] and report['exampleConforms']
    assert report['focusNodeCount'] == 1 and report['profileSnapshotSha256'] == profile['sha256']
    assert report['policy'] == POLICY


def test_malformed_profile_and_unsupported_sparql_are_not_silently_accepted(client):
    for addition in ['demo:NameShape sh:minCount "wrong datatype".',
                     'demo:ProductShape sh:sparql [ sh:select "SELECT ?this WHERE { SERVICE <http://127.0.0.1> { ?this ?p ?o } }" ].',
                     'demo:ProductShape sh:inventedConstraint true.']:
        data = profile_input(); data['artifact']['content'] += '\n' + addition
        response = client.post('/api/v1/profile-snapshots', json=data)
        assert response.status_code == 201, response.text
        profile = response.json()
        assert profile['verificationStatus'] == 'needsAttention'
        assert not profile['profileValidation']['conforms']
        draft = create(client, body() | {'profileSnapshotId': profile['id']})
        assert draft['semanticValidation']['status'] == 'invalid'
        assert submit(client, draft).status_code == 422


def test_dependency_nested_shapes_and_code_list_constraints_are_applied(client):
    data = profile_input()
    data['artifact']['content'] += '\ndemo:ProductShape sh:property [ sh:path <urn:address>; sh:node <urn:AddressShape>; sh:minCount 1 ].'
    data['dependencyArtifacts'] = [{'uri':'urn:AddressShape','artifact':{'serialization':'turtle','content':
        '@prefix sh:<http://www.w3.org/ns/shacl#>. <urn:AddressShape> a sh:NodeShape; sh:property [ sh:path <urn:postalCode>; sh:in ("00100" "00200"); sh:minCount 1 ].'}}]
    profile = client.post('/api/v1/profile-snapshots', json=data).json()
    content = EXAMPLE + '\n<urn:synthetic:company:1> <urn:address> [ <urn:postalCode> "99999" ].'
    draft = create(client, body() | {'profileSnapshotId':profile['id'], 'syntheticExample':with_example(content)})
    assert draft['semanticValidation']['status'] == 'invalid'
    assert any(item['ruleId'].endswith('InConstraintComponent') for item in draft['semanticValidation']['results'])
    fixed = change(client, draft, body() | {'profileSnapshotId':profile['id'], 'syntheticExample':with_example(content.replace('99999','00100'))})
    assert fixed['semanticValidation']['status'] == 'conforms'


def test_network_contexts_entities_and_unconfirmed_examples_block(client):
    profile = import_profile(client)
    for content,fmt in [('{"@context":"https://example.org/secret","@id":"urn:demo"}', 'jsonld'),
                        ('<!DOCTYPE r [<!ENTITY x SYSTEM "file:///etc/passwd">]><r/>', 'rdfxml')]:
        draft = create(client, body() | {'profileSnapshotId':profile['id'], 'syntheticExample':with_example(content,fmt)})
        assert draft['semanticValidation']['status'] == 'error'
        assert submit(client, draft).status_code == 422
        assert 'passwd' not in str(draft['semanticValidation'])
    for example in [with_example(EXAMPLE)|{'synthetic':False}, {'content':EXAMPLE,'serialization':'turtle'}, with_example('a'*100001)]:
        assert client.post('/api/v1/products', json=body()|{'syntheticExample':example}).status_code == 422


def test_reports_are_server_owned_hash_bound_and_keep_prior_publications(client):
    profile = import_profile(client)
    assert client.post('/api/v1/products',json=body()|{'semanticValidation':{'status':'conforms'}}).status_code == 422
    draft = create(client, body() | {'profileSnapshotId':profile['id']})
    first = publish(client, draft)
    assert first['semanticValidation']['exampleSha256']
    stored = client.get(f"/api/v1/products/{draft['id']}/draft").json()
    next_draft = client.post(f"/api/v1/products/{draft['id']}/drafts", headers={'If-Match':stored['etag']}).json()
    bad = change(client,next_draft,body()|{'profileSnapshotId':profile['id'],'syntheticExample':with_example(EXAMPLE.replace('"Synteettinen Esimerkki Oy"','123'))})
    assert bad['semanticValidation']['status'] == 'invalid' and submit(client,bad).status_code == 422
    assert client.get(f"/api/v1/products/{draft['id']}/versions/1.0.0").json() == first
    assert client.get(f"/api/v1/products/{draft['id']}/export").json()['semanticValidation'] == first['semanticValidation']
    with TestClient(app) as anonymous:
        assert anonymous.get(f"/api/v1/products/{draft['id']}/draft").status_code == 401
        assert anonymous.post(f"/api/v1/drafts/{draft['draftId']}/validate").status_code == 401


def test_legacy_draft_missing_report_needs_resave(client):
    profile = import_profile(client)
    draft = create(client, body() | {'profileSnapshotId':profile['id']})
    with Session(engine) as session:
        stored = session.get(Draft, UUID(draft['draftId']))
        content = dict(stored.content); content.pop('semanticValidation')
        stored.content = content; session.commit()
    assert submit(client,draft).status_code == 422
    # A read-only preview computes a new result but never alters content, revision or approval.
    before = client.get(f"/api/v1/products/{draft['id']}/draft").json()
    preview = client.post(f"/api/v1/drafts/{draft['draftId']}/validate").json()
    assert preview['semanticValidation']['status'] == 'conforms'
    assert client.get(f"/api/v1/products/{draft['id']}/draft").json() == before
    assert submit(client,before).status_code == 422
    fixed = change(client,before,body()|{'profileSnapshotId':profile['id']})
    assert submit(client,fixed).status_code == 200


def test_inactive_shapes_do_not_give_empty_success(client):
    data=profile_input();data['artifact']['content']+='\ndemo:ProductShape sh:deactivated true.'
    profile=client.post('/api/v1/profile-snapshots',json=data).json()
    draft=create(client,body()|{'profileSnapshotId':profile['id']})
    assert draft['semanticValidation']['status']=='invalid'
    assert submit(client,draft).status_code==422


def test_expensive_regular_expression_is_bounded_and_fails_closed(client):
    data=profile_input();data['artifact']['content']+='\ndemo:NameShape sh:pattern "(a+)+$".'
    profile=client.post('/api/v1/profile-snapshots',json=data).json()
    content=EXAMPLE.replace('Synteettinen Esimerkki Oy','a'*10000+'!')
    draft=create(client,body()|{'profileSnapshotId':profile['id'],'syntheticExample':with_example(content)})
    assert draft['semanticValidation']['status']=='error'
    assert draft['semanticValidation']['results'][0]['ruleId']=='VALIDATION_RESOURCE_LIMIT'
    assert submit(client,draft).status_code==422
    assert client.get('/health/ready').status_code==200


def test_uploaded_utf8_content_and_whitespace_are_preserved(client):
    import hashlib
    data=profile_input();original='\n'+data['artifact']['content']+'\n'
    data['artifact']['content']=original
    profile=client.post('/api/v1/profile-snapshots',json=data).json()
    manifest=client.get('/api/v1/profile-snapshots/'+profile['id']).json()['manifest']
    assert manifest['sourceArtifacts'][0]['content']==original
    assert manifest['sourceArtifacts'][0]['sha256']==hashlib.sha256(original.encode()).hexdigest()
    example='\n'+EXAMPLE+'\n'
    draft=create(client,body()|{'profileSnapshotId':profile['id'],'syntheticExample':with_example(example)})
    assert draft['syntheticExample']['content']==example
    assert draft['semanticValidation']['status']=='conforms'
    assert draft['semanticValidation']['exampleSha256']==hashlib.sha256(example.encode()).hexdigest()


def test_named_jsonld_graphs_are_rejected_instead_of_losing_constraints(client):
    import json
    data=profile_input()
    document=json.loads(Graph().parse(data=data['artifact']['content'],format='turtle').serialize(format='json-ld'))
    document.append({'@id':'urn:hidden-graph','@graph':[{'@id':'urn:hidden','urn:constraint':'must not disappear'}]})
    data['artifact']={'serialization':'jsonld','content':json.dumps(document)}
    assert client.post('/api/v1/profile-snapshots',json=data).status_code==422
    profile=import_profile(client)
    example=json.loads(Graph().parse(data=EXAMPLE,format='turtle').serialize(format='json-ld'))
    example.append({'@id':'urn:hidden-graph','@graph':[{'@id':'urn:hidden','urn:secret':'synthetic'}]})
    draft=create(client,body()|{'profileSnapshotId':profile['id'],'syntheticExample':with_example(json.dumps(example),'jsonld')})
    assert draft['semanticValidation']['status']=='error'
    assert submit(client,draft).status_code==422
