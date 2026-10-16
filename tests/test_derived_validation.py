"""Real schema dialects, semantic coverage and publication gating, offline."""
import json
from pathlib import Path
from uuid import uuid4
import pytest
from fastapi.testclient import TestClient
from apps.api.main import app
from helpers import body,profile_input,create,change,publish,ORG

SCHEMA=json.loads(Path('fixtures/derived-schema-demo.json').read_text())
MAPPINGS=json.loads(Path('fixtures/derived-mappings-demo.json').read_text())
EXAMPLE=Path('fixtures/derived-example-demo.json').read_text()


def profile_with(client,doc=None,kind='jsonSchema',mappings=None,pointer=''):
    data=profile_input()
    data['derivedArtifacts']=[{'serialization':kind,'content':json.dumps(SCHEMA if doc is None else doc),
        'semanticMappings':MAPPINGS if mappings is None else mappings,'schemaPointer':pointer}]
    response=client.post('/api/v1/profile-snapshots',json=data)
    assert response.status_code==201,response.text
    profile=response.json()
    manifest=client.get('/api/v1/profile-snapshots/'+profile['id']).json()['manifest']
    artifact=manifest['derivedArtifacts'][0]
    return profile,artifact


def ready(client,profile,artifact,content=EXAMPLE):
    return create(client,body()|{'profileSnapshotId':profile['id'],'derivedExamples':[{'artifactId':artifact['id'],'content':content,'synthetic':True}]})


def submit(client,draft):return client.post(f"/api/v1/drafts/{draft['draftId']}/submit",headers={'If-Match':draft['etag']})


@pytest.mark.parametrize('dialect',['http://json-schema.org/draft-04/schema#','http://json-schema.org/draft-06/schema#','http://json-schema.org/draft-07/schema#','https://json-schema.org/draft/2019-09/schema','https://json-schema.org/draft/2020-12/schema'])
def test_original_dialects_and_direct_coverage(client,dialect):
    profile,artifact=profile_with(client,SCHEMA|{'$schema':dialect})
    assert artifact['dialect']==dialect
    draft=ready(client,profile,artifact)
    report=draft['derivedValidation'];assert report['status']=='conforms',report
    assessment=report['artifacts'][0]
    assert assessment['schemaValid'] and assessment['exampleValid'] and assessment['dialect']==dialect
    assert assessment['coverage'][0]['status']=='direct'
    assert report['profileSnapshotSha256']==profile['sha256']
    assert submit(client,draft).status_code==200


@pytest.mark.parametrize('version',['3.0.3','3.1.1'])
def test_openapi_original_version_local_refs_and_selected_schema(client,version):
    component={key:value for key,value in SCHEMA.items() if key!='$schema'}
    doc={'openapi':version,'info':{'title':'Synthetic fixture','version':'1'},'paths':{},
         'components':{'schemas':{'Company':component,'CompanyAlias':{'$ref':'#/components/schemas/Company'}}}}
    profile,artifact=profile_with(client,doc,'openapi',pointer='/components/schemas/CompanyAlias')
    draft=ready(client,profile,artifact)
    assert draft['derivedValidation']['status']=='conforms',draft['derivedValidation']
    assert draft['derivedValidation']['artifacts'][0]['dialect']==version


@pytest.mark.parametrize('content,rule', [('{}','JSON_SCHEMA_required'),('{"companyName":3}','JSON_SCHEMA_type'),('{"companyName":"Testi","extra":true}','JSON_SCHEMA_additionalProperties')])
def test_invalid_json_examples_block_publication(client,content,rule):
    profile,artifact=profile_with(client);draft=ready(client,profile,artifact,content)
    report=draft['derivedValidation'];assert report['status']=='invalid'
    assert any(item['ruleId']==rule for item in report['artifacts'][0]['results'])
    assert submit(client,draft).status_code==422


def test_missing_mapping_and_cardinality_or_datatype_conflicts(client):
    for schema,mappings in [(SCHEMA,[]),(SCHEMA|{'required':[]},MAPPINGS),
                             (SCHEMA|{'properties':{'companyName':{'type':'integer'}}},MAPPINGS)]:
        profile,artifact=profile_with(client,schema,mappings=mappings)
        draft=ready(client,profile,artifact)
        assert draft['derivedValidation']['status']=='invalid'
        assert any(item['ruleId'] in ('MAPPING_MISSING','MAPPING_CONFLICT') for item in draft['derivedValidation']['artifacts'][0]['results'])
        assert submit(client,draft).status_code==422


def test_schema_structure_dialect_and_remote_refs_fail_closed(client):
    for schema in [SCHEMA|{'$schema':'https://unknown.example/dialect'},SCHEMA|{'type':42},
                   SCHEMA|{'properties':{'companyName':{'$ref':'https://example.org/schema'}}},
                   SCHEMA|{'properties':{'companyName':{'$ref':'file:///etc/passwd'}}},
                   {key:value for key,value in SCHEMA.items() if key!='$schema'}]:
        profile,artifact=profile_with(client,schema)
        draft=ready(client,profile,artifact)
        assert draft['derivedValidation']['status']=='invalid'
        assert submit(client,draft).status_code==422


def test_openapi_structure_nullable_and_unsupported_versions(client):
    doc={'openapi':'3.0.3','info':{'title':'Demo','version':'1'},'paths':{},'components':{'schemas':{
        'Company':{'type':'object','properties':{'companyName':{'type':'string','nullable':True}},'required':['companyName'],'additionalProperties':False}}}}
    profile,artifact=profile_with(client,doc,'openapi',pointer='/components/schemas/Company')
    draft=ready(client,profile,artifact,'{"companyName":null}')
    assert draft['derivedValidation']['artifacts'][0]['exampleValid'] # OAS30 nullable is preserved, never converted to draft 2020.
    assert draft['derivedValidation']['status']=='invalid' # This SHACL datatype does not permit null.
    for changed in [doc|{'openapi':'3.2.0'},doc|{'info':{'title':'Missing version'}}]:
        profile,artifact=profile_with(client,changed,'openapi',pointer='/components/schemas/Company')
        assert ready(client,profile,artifact)['derivedValidation']['status']=='invalid'


def test_json_refs_stay_local_and_unsupported_composition_is_visible(client):
    schema=SCHEMA|{'$id':'https://example.org/synthetic/schema','definitions':{'Name':{'type':'string'}},'properties':{'companyName':{'$ref':'#/definitions/Name'}}}
    profile,artifact=profile_with(client,schema)
    assert ready(client,profile,artifact)['derivedValidation']['status']=='conforms'
    schema=SCHEMA|{'properties':{'companyName':{'allOf':[{'type':'string'}]}}}
    profile,artifact=profile_with(client,schema)
    report=ready(client,profile,artifact)['derivedValidation']
    assert report['artifacts'][0]['exampleValid'] and report['status']=='invalid'
    assert any(item['ruleId']=='MAPPING_UNASSESSED' for item in report['artifacts'][0]['results'])


def test_missing_unknown_and_unconfirmed_examples_and_forged_reports(client):
    profile,artifact=profile_with(client)
    draft=create(client,body()|{'profileSnapshotId':profile['id']})
    assert submit(client,draft).status_code==422
    unknown=artifact|{'id':str(uuid4())};assert ready(client,profile,unknown)['derivedValidation']['status']=='invalid'
    for extra in [{'derivedValidation':{'status':'conforms'}},
                  {'derivedExamples':[{'artifactId':artifact['id'],'content':EXAMPLE,'synthetic':False}]},
                  {'derivedExamples':[{'artifactId':artifact['id'],'content':EXAMPLE}]}]:
        assert client.post('/api/v1/products',json=body()|extra).status_code==422
    with TestClient(app) as anonymous:
        assert anonymous.get('/api/v1/profile-snapshots/'+profile['id']).status_code==404
        assert anonymous.post('/api/v1/products',json=body()).status_code==401


def test_new_draft_cannot_change_prior_reports_and_schema_download(client):
    profile,artifact=profile_with(client)
    draft=ready(client,profile,artifact);first=publish(client,draft)
    assert first['derivedValidation']['status']=='conforms'
    url=f"/api/v1/profile-snapshots/{profile['id']}/artifacts/{artifact['id']}"
    assert json.loads(client.get(url).text)==SCHEMA
    private=client.get(f"/api/v1/products/{draft['id']}/draft").json()
    next_draft=client.post(f"/api/v1/products/{draft['id']}/drafts",headers={'If-Match':private['etag']}).json()
    bad=change(client,next_draft,body()|{'profileSnapshotId':profile['id'],'derivedExamples':[{'artifactId':artifact['id'],'synthetic':True,'content':'{}'}]})
    assert bad['derivedValidation']['status']=='invalid' and submit(client,bad).status_code==422
    assert client.get(f"/api/v1/products/{draft['id']}/versions/1.0.0").json()==first


def test_array_cardinality_and_literal_code_lists(client):
    source=profile_input();source['artifact']['content']=source['artifact']['content'].replace('sh:maxCount 1','sh:maxCount 3')
    array=SCHEMA|{'properties':{'companyName':{'type':'array','items':{'type':'string'},'minItems':1,'maxItems':3}}}
    source['derivedArtifacts']=[{'serialization':'jsonSchema','content':json.dumps(array),'semanticMappings':MAPPINGS}]
    response=client.post('/api/v1/profile-snapshots',json=source);assert response.status_code==201
    profile=response.json();artifact=client.get('/api/v1/profile-snapshots/'+profile['id']).json()['manifest']['derivedArtifacts'][0]
    assert ready(client,profile,artifact,'{"companyName":["A","B"]}')['derivedValidation']['status']=='conforms'
    source=profile_input();source['artifact']['content']+='\ndemo:NameShape sh:in ("Synteettinen Esimerkki Oy" "B").'
    for values,expected in [(['Synteettinen Esimerkki Oy','B'],'conforms'),(['Synteettinen Esimerkki Oy'],'invalid')]:
        schema=SCHEMA|{'properties':{'companyName':{'type':'string','enum':values}}}
        source['derivedArtifacts']=[{'serialization':'jsonSchema','content':json.dumps(schema),'semanticMappings':MAPPINGS}]
        profile=client.post('/api/v1/profile-snapshots',json=source).json()
        artifact=client.get('/api/v1/profile-snapshots/'+profile['id']).json()['manifest']['derivedArtifacts'][0]
        assert ready(client,profile,artifact)['derivedValidation']['status']==expected


def test_non_json_constants_duplicate_keys_and_byte_limits(client):
    profile,artifact=profile_with(client)
    for content in ['{"companyName": NaN}','{"companyName":"A","companyName":"B"}']:
        assert ready(client,profile,artifact,content)['derivedValidation']['status']=='invalid'
    assert client.post('/api/v1/products',json=body()|{'derivedExamples':[{'artifactId':artifact['id'],'synthetic':True,'content':'ä'*60000}]}).status_code==422
