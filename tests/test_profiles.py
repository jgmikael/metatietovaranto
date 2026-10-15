import json
from pathlib import Path
from uuid import UUID
from rdflib import Graph
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from conftest import authenticate
from apps.api.main import app,engine
from apps.api.models import ProfileSnapshot
from apps.api.profiles import ProfileInput,snapshot_manifest,checksum,fetch_artifact
from helpers import profile_input,import_profile,ORG


def test_rdf_serializations_preserve_same_graph_and_profile_identity(client):
    source=profile_input();graph=Graph().parse(data=source['artifact']['content'],format='turtle');results=[]
    for serialization,format in [('turtle','turtle'),('rdfxml','xml'),('jsonld','json-ld')]:
        data=source|{'artifact':{'serialization':serialization,'content':graph.serialize(format=format)}}
        response=client.post('/api/v1/profile-snapshots',json=data)
        assert response.status_code==201,response.text
        results.append(response.json())
    assert len({row['graphHash'] for row in results})==1
    assert len({row['profileId'] for row in results})==1
    assert all(row['elements'][0]['shapeUri']!=row['elements'][0]['subjectClassUri'] for row in results)
    full=client.get('/api/v1/profile-snapshots/'+results[0]['id']).json()['manifest']
    artifact=full['sourceArtifacts'][0]
    fetched=client.get(f"/api/v1/profile-snapshots/{results[0]['id']}/artifacts/{artifact['id']}")
    assert fetched.text==artifact['content'] and 'attachment' in fetched.headers['content-disposition']


def test_derived_schema_preserves_dialect_but_cannot_replace_shacl(client):
    data=profile_input();data['artifact']={'serialization':'jsonSchema','content':json.dumps({'$schema':'http://json-schema.org/draft-07/schema#','type':'object'})}
    response=client.post('/api/v1/profile-snapshots',json=data);assert response.status_code==201
    full=client.get('/api/v1/profile-snapshots/'+response.json()['id']).json()['manifest']
    assert full['derivedArtifacts'][0]['dialect']=='http://json-schema.org/draft-07/schema#'
    assert full['shapesArtifactId'] is None and full['verificationStatus']=='needsAttention'


def test_context_and_owl_are_not_ready_profiles(client):
    for content in ['{"@context":{"demo":"https://example.org/demo/"}}','@prefix owl:<http://www.w3.org/2002/07/owl#>. <https://example.org/model> a owl:Ontology.']:
        data=profile_input();data['artifact']={'serialization':'jsonld' if content.startswith('{') else 'turtle','content':content}
        response=client.post('/api/v1/profile-snapshots',json=data);assert response.status_code==201,response.text
        assert response.json()['verificationStatus']=='needsAttention'


def test_unresolved_imports_and_complex_paths_are_preserved(client):
    data=profile_input();data['artifact']['content']+='\n<https://example.org/metatietovaranto/demo/profile> <http://www.w3.org/2002/07/owl#imports> <https://external.example/model>.\n'
    data['artifact']['content']+='\n<https://example.org/metatietovaranto/demo/ProductShape> <http://www.w3.org/ns/shacl#property> [ <http://www.w3.org/ns/shacl#path> ( <urn:a> <urn:b> ) ].'
    response=client.post('/api/v1/profile-snapshots',json=data);assert response.status_code==201
    result=response.json();assert result['verificationStatus']=='needsAttention'
    assert any(element['complexPath'] for element in result['elements'])
    manifest=client.get('/api/v1/profile-snapshots/'+result['id']).json()['manifest']
    assert manifest['dependencies'][0]['status']=='unresolved' and '( <urn:a> <urn:b> )' in manifest['sourceArtifacts'][0]['content']


def test_profile_security_xml_remote_context_and_cross_org(client):
    for serialization,content in [('rdfxml','<!DOCTYPE r [<!ENTITY x SYSTEM "file:///etc/passwd">]><r/>'),('jsonld','{"@context":"http://127.0.0.1/private"}')]:
        data=profile_input()|{'artifact':{'serialization':serialization,'content':content}}
        assert client.post('/api/v1/profile-snapshots',json=data).status_code==422
    profile=import_profile(client)
    with TestClient(app) as outsider:
        authenticate(outsider,'unassigned')
        assert outsider.get('/api/v1/profile-snapshots/'+profile['id']).status_code==404
        assert outsider.post('/api/v1/profile-snapshots',json=profile_input()).status_code==403


def test_link_and_file_are_alternatives_and_snapshot_is_locked(monkeypatch):
    import apps.api.profiles as profiles
    original=profile_input()
    monkeypatch.setattr(profiles,'fetch_artifact',lambda url,serialization: profiles.ArtifactInput.model_validate(original['artifact']|{'sourceUrl':str(url)}))
    linked={k:v for k,v in original.items() if k!='artifact'}|{'ingestionMethod':'link','sourceUrl':'https://iri.suomi.fi/model/demo.ttl'}
    a=snapshot_manifest(ProfileInput.model_validate(original));b=snapshot_manifest(ProfileInput.model_validate(linked))
    assert a['profileUri']==b['profileUri'] and a['graphHash']==b['graphHash']
    old_hash=checksum(a);original['artifact']['content']+='\n<urn:new> <urn:predicate> <urn:object>.'
    assert checksum(a)==old_hash


def test_ssrf_hosts_and_tokenized_issuer_links_are_rejected(client):
    for url in ['http://iri.suomi.fi/model','https://localhost/model','https://127.0.0.1/model','https://evil.example/model']:
        data={k:v for k,v in profile_input().items() if k!='artifact'}|{'ingestionMethod':'link','sourceUrl':url}
        assert client.post('/api/v1/profile-snapshots',json=data).status_code==422
    from helpers import body
    for url in ['https://issuer.example.org/request','openid-credential-offer://offer','https://issuer.fi/request?pre-authorized_code=secret','https://user:pass@issuer.fi/request']:
        assert client.post('/api/v1/products',json=body()|{'issuance':{'issuanceInitiationUrl':url}},headers={'Idempotency-Key':'issuer-check'}).status_code==422
