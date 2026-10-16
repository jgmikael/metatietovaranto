"""Typed parallel formats, shared profile and nested mapping metadata, no issuance."""
import copy,json
from pathlib import Path
from uuid import uuid4,UUID
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi.testclient import TestClient
import pytest
from apps.api.main import app,engine
from apps.api.models import Draft,Product
from helpers import body,profile_input,create,change,publish,import_profile,ORG


def definitions():return json.loads(Path('fixtures/distributions-demo.json').read_text())

def draft_with(client,items=None,profile=None):
    profile=profile or import_profile(client)
    return create(client,body()|{'profileSnapshotId':profile['id'],'distributions':items or definitions()})


def submit(client,draft):return client.post(f"/api/v1/drafts/{draft['draftId']}/submit",headers={'If-Match':draft['etag']})


def test_three_formats_roundtrip_share_profile_and_new_versions_are_immutable(client):
    draft=draft_with(client)
    assert draft['distributionValidation']['status']=='conforms',draft['distributionValidation']
    assert draft['primaryDistributionId']==draft['distributions'][1]['id']
    assert {item['type'] for item in draft['distributions']}=={'jsonApi','w3cVc','sdJwtVc'}
    assert {item['profileSnapshotId'] for item in draft['distributions']}=={draft['profileSnapshotId']}
    first=publish(client,draft)
    assert len(first['distributionBindings'])==3
    assert {item['productVersion'] for item in first['distributionBindings']}=={'1.0.0'}
    assert {item['profileSnapshotSha256'] for item in first['distributionBindings']}=={first['semanticProfileSnapshot']['sha256']}
    private=client.get(f"/api/v1/products/{draft['id']}/draft").json()
    new=client.post(f"/api/v1/products/{draft['id']}/drafts",headers={'If-Match':private['etag']}).json()
    changed=definitions();changed[2]['mapping']['version']='1.1.0';changed[2]['sdJwt']['holderBinding']='optional'
    updated=change(client,new,body()|{'profileSnapshotId':draft['profileSnapshotId'],'distributions':changed})
    assert updated['status']=='draft' and updated['contentHash']!=first['contentHash']
    assert client.get(f"/api/v1/products/{draft['id']}/versions/1.0.0").json()==first
    assert client.get(f"/api/v1/products/{draft['id']}/export?format=jsonld").json()['demo:distributions']


def test_active_services_need_full_metadata_and_planned_does_not_invent_service(client):
    items=definitions()
    for item in items:item['availability']='sandbox'
    draft=draft_with(client,items)
    assert draft['distributionValidation']['status']=='invalid' and submit(client,draft).status_code==422
    assert any(item['ruleId']=='API_METADATA_REQUIRED' for item in draft['distributionValidation']['results'])
    assert any(item['ruleId']=='CREDENTIAL_METADATA_REQUIRED' for item in draft['distributionValidation']['results'])
    assert draft_with(client)['distributionValidation']['status']=='conforms'


@pytest.mark.parametrize('mutation', ['format','token','context','profile','primary','extra_secret','duplicate'])
def test_invalid_technical_choices_and_different_snapshots_rejected(client,mutation):
    items=definitions();profile=import_profile(client)
    data=body()|{'profileSnapshotId':profile['id'],'distributions':items}
    if mutation=='format':items[2]['format']='application/vc+ld+json'
    elif mutation=='token':items[1]['credential']['initiationUrl']='https://issuer.fi/start?pre-authorized_code=secret'
    elif mutation=='context':items[2]['sdJwt']['contexts']=['https://example.org/context']
    elif mutation=='profile':items[2]['profileSnapshotId']=str(uuid4())
    elif mutation=='primary':data['primaryDistributionId']=str(uuid4())
    elif mutation=='extra_secret':items[0]['api']['accessToken']='secret'
    elif mutation=='duplicate':items[2]['id']=items[1]['id']
    assert client.post('/api/v1/products',json=data,headers={'Idempotency-Key':str(uuid4())}).status_code==422


def test_mapping_conflicts_uncovered_claims_and_reserved_sdjwt_claims_block_review(client):
    for mutate in [lambda items:items[2]['mapping']['entries'][0].update(fieldPath='/vct'),
                   lambda items:items[0]['mapping']['entries'][0].update(datatype='http://www.w3.org/2001/XMLSchema#integer'),
                   lambda items:items[1]['mapping'].update(entries=[]),
                   lambda items:items[2]['mapping']['entries'][0].update(fieldPath='/company_name/*')]:
        items=definitions();mutate(items);draft=draft_with(client,items)
        assert draft['distributionValidation']['status']=='invalid'
        assert submit(client,draft).status_code==422


def test_same_openid_issuer_can_support_two_distinct_configurations(client):
    items=definitions()
    for item in items[1:]:item['credential']['credentialIssuer']='https://issuer.fi/'
    assert draft_with(client,items)['distributionValidation']['status']=='conforms'
    items[2]['credential']['configurationIds']=items[1]['credential']['configurationIds']
    draft=draft_with(client,items)
    assert any(item['ruleId']=='CONFIGURATION_AMBIGUOUS' for item in draft['distributionValidation']['results'])


def test_nested_objects_datatypes_and_multivalued_fields(client):
    source=profile_input()
    source['artifact']['content']+='''\n@prefix ex:<urn:example:>.\ndemo:ProductShape sh:property [sh:path ex:addresses;sh:node ex:AddressShape;sh:class ex:Address;sh:minCount 0].
ex:AddressShape a sh:NodeShape;sh:targetClass ex:Address;sh:property [sh:path ex:postalCode;sh:datatype xsd:string;sh:minCount 1;sh:maxCount 1].'''
    profile=client.post('/api/v1/profile-snapshots',json=source).json()
    items=definitions()
    for item in items:
        prefix='/credentialSubject' if item['type']=='w3cVc' else ''
        template=item['mapping']['entries'][0]
        extra=[template|{'semanticPath':['urn:example:addresses'],'fieldPath':prefix+'/addresses/*','valueKind':'object','datatype':None,'classUri':'urn:example:Address','minCount':0,'maxCount':None},
               template|{'semanticPath':['urn:example:addresses','urn:example:postalCode'],'fieldPath':prefix+'/addresses/*/postal_code'},
               template|{'shapeUri':'urn:example:AddressShape','semanticPath':['urn:example:postalCode'],'fieldPath':prefix+'/address_content/postal_code'}]
        item['mapping']['entries']+=extra
    draft=draft_with(client,items,profile)
    assert draft['distributionValidation']['status']=='conforms',draft['distributionValidation']
    items[2]['mapping']['entries'][2]['fieldPath']='/wrong_parent/postal_code'
    broken=draft_with(client,items,profile)
    assert any(item['ruleId']=='MAPPING_NESTING' for item in broken['distributionValidation']['results'])


def test_additive_synthetic_example_never_resets_changes_or_returns_after_deletion(client):
    product_id='00000000-0000-4000-8000-000000000004'
    draft=client.get(f'/api/v1/products/{product_id}/draft').json()
    assert draft['distributionValidation']['status']=='conforms',draft
    data=body()|{'title':'Käyttäjän muokkaama kolmen toimitustavan demo','profileSnapshotId':draft['profileSnapshotId'],
        'distributions':draft['distributions'],'derivedExamples':draft['derivedExamples']}
    modified=change(client,draft,data)
    with TestClient(app):pass
    assert client.get(f'/api/v1/products/{product_id}/draft').json()==modified
    assert client.delete(f'/api/v1/products/{product_id}',headers={'If-Match':modified['etag']}).status_code==204
    with TestClient(app):pass
    assert client.get(f'/api/v1/products/{product_id}/draft').status_code==404


def test_three_active_formats_validate_without_contacting_any_service(client):
    sample=client.get('/api/v1/products/00000000-0000-4000-8000-000000000004/draft').json()
    items=sample['distributions']
    for item in items:
        item['availability']='sandbox'
        if item['type']=='jsonApi':
            item['api']['serviceUrl']='https://provider.fi/company'
            item['api']['descriptionUrl']='https://provider.fi/docs'
        else:
            item['credential']['credentialIssuer']='https://issuer.fi/'
            item['credential']['initiationUrl']='https://issuer.fi/start?configuration='+item['type']
    draft=create(client,body()|{'profileSnapshotId':sample['profileSnapshotId'],'distributions':items,'derivedExamples':sample['derivedExamples']})
    assert draft['distributionValidation']['status']=='conforms',draft['distributionValidation']
    assert submit(client,draft).status_code==200


def test_legacy_payload_cannot_silently_drop_new_distribution_collection(client):
    draft=draft_with(client)
    response=client.put('/api/v1/products/'+draft['id'],json=body()|{'profileSnapshotId':draft['profileSnapshotId']},headers={'If-Match':draft['etag']})
    assert response.status_code==422
    assert client.get('/api/v1/products/'+draft['id']+'/draft').json()==draft


def test_mapping_change_requires_a_new_mapping_version(client):
    from test_publication import approve
    from conftest import authenticate
    first=draft_with(client);publish(client,first)
    private=client.get('/api/v1/products/'+first['id']+'/draft').json()
    next_draft=client.post('/api/v1/products/'+first['id']+'/drafts',headers={'If-Match':private['etag']}).json()
    items=definitions();items[0]['mapping']['entries'][0]['fieldPath']='/new_company_name'
    updated=change(client,next_draft,body()|{'profileSnapshotId':first['profileSnapshotId'],'distributions':items})
    approved=approve(client,submit(client,updated).json())
    url='/api/v1/drafts/'+first['draftId']+'/publish'
    result=client.post(url,json={'version':'1.1.0'},headers={'If-Match':approved['etag'],'Idempotency-Key':str(uuid4())})
    assert result.status_code==409 and 'Mapping' in result.text
    authenticate(client,'mapping-version-editor',[UUID(ORG)])
    items[0]['mapping']['version']='1.1.0'
    fixed=change(client,approved,body()|{'profileSnapshotId':first['profileSnapshotId'],'distributions':items})
    approved=approve(client,submit(client,fixed).json())
    assert client.post(url,json={'version':'1.1.0'},headers={'If-Match':approved['etag'],'Idempotency-Key':str(uuid4())}).status_code==200


def test_json_api_mapping_paths_must_exist_in_referenced_technical_schemas(client):
    sample=client.get('/api/v1/products/00000000-0000-4000-8000-000000000004/draft').json()
    items=sample['distributions'];items[0]['mapping']['entries'][0]['fieldPath']='/missing_field'
    draft=create(client,body()|{'profileSnapshotId':sample['profileSnapshotId'],'distributions':items,'derivedExamples':sample['derivedExamples']})
    assert any(item['ruleId']=='API_SCHEMA_MAPPING' for item in draft['distributionValidation']['results'])
    assert submit(client,draft).status_code==422
