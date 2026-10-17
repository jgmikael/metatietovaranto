"""Synthetic content conversion with PostgreSQL authorization and immutable old data."""
import copy
import hashlib
import json
from uuid import UUID, uuid4

import pytest
from rdflib import Graph
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from apps.api.main import engine
from apps.api.models import AuditEvent, ProductVersion
from conftest import authenticate
from helpers import ORG, body, create, profile_input, publish

DEMO = '00000000-0000-4000-8000-000000000004'
P = 'https://example.org/metatietovaranto/demo/'
XSD = 'http://www.w3.org/2001/XMLSchema#'


def sample(client):return client.get('/api/v1/products/'+DEMO+'/draft').json()


def payload(draft, names=None):
    values = names or ['Synteettinen Esimerkki Oy']*3
    objects = [{'companyName':values[0]}, {'credentialSubject':{'companyName':values[1]}}, {'company_name':values[2]}]
    return {'examples':[{'distributionId':item['id'], 'content':json.dumps(value), 'synthetic':True}
                        for item, value in zip(draft['distributions'], objects)]}


def preview(client, draft, data=None, **kwargs):
    return client.post('/api/v1/drafts/'+draft['draftId']+'/conversion-preview',
        json=data or payload(draft), headers={'If-Match':draft['etag'], **kwargs})


def test_three_formats_same_graph_without_writing_draft_approval_or_publication(client):
    draft = sample(client)
    with Session(engine) as session:
        audit_before=session.scalar(select(func.count()).select_from(AuditEvent))
        versions_before=session.scalar(select(func.count()).select_from(ProductVersion))
    response = preview(client, draft)
    assert response.status_code == 200, response.text
    report=response.json()
    assert report['status']=='conforms',report
    assert report['comparison']['status']=='sameGraph'
    assert len({row['graphSha256'] for row in report['examples']})==1
    assert report['draftRevision']==draft['revision'] and report['draftContentHash']==draft['contentHash']
    assert report['profileSnapshotSha256']==draft['profileSnapshot']['sha256']
    assert report['examples'][0]['structureValidation']['status']=='conforms'
    assert all(row['structureValidation']['status']=='notAssessed' for row in report['examples'][1:])
    for row in report['examples']:
        assert row['semanticValidation']['status']=='conforms' and row['mappingVersion']=='1.0.0'
        assert len(Graph().parse(data=row['rdf'],format='turtle'))==2
    assert client.get('/api/v1/products/'+DEMO+'/draft').json()==draft
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(AuditEvent))==audit_before
        assert session.scalar(select(func.count()).select_from(ProductVersion))==versions_before


def test_valid_but_different_values_not_reported_equivalent(client):
    draft=sample(client)
    report=preview(client,draft,payload(draft,['A','B','A'])).json()
    assert all(row['status']=='conforms' for row in report['examples']),report
    assert report['status']=='different' and report['comparison']['status']=='differentGraphs'


def test_single_example_not_claimed_compared_and_byte_hash_preserved(client):
    draft=sample(client);data=payload(draft);data['examples']=data['examples'][1:2]
    data['examples'][0]['content']=' \n'+data['examples'][0]['content']+' \n'
    report=preview(client,draft,data).json()
    assert report['status']=='conforms' and report['comparison']['status']=='notCompared'
    assert report['examples'][0]['exampleSha256']==hashlib.sha256(data['examples'][0]['content'].encode()).hexdigest()


@pytest.mark.parametrize('content,rule',[
    ('{"company_name":null}','JSON_DATATYPE'),
    ('{"company_name":42}','JSON_DATATYPE'),
    ('{}','JSON_CARDINALITY'),
    ('{"company_name":"A","extra":{}}','JSON_UNMAPPED'),
    ('{"company_name":"A","extra":[]}','JSON_UNMAPPED'),
    ('{"company_name":"A","_sd":["digest"]}','CREDENTIAL_MATERIAL'),
    ('{"company_name":"A","proof":{}}','CREDENTIAL_MATERIAL'),
    ('"eyJhbGciOi...signature"','JSON_OBJECT'),
    ('{"company_name":"A","company_name":"B"}','JSON_SYNTAX'),
    ('{"company_name":NaN}','JSON_SYNTAX'),
    ('{"company_name":1e999}','JSON_NUMBER'),
])
def test_invalid_lossy_or_credential_input_fails_closed(client,content,rule):
    draft=sample(client);data=payload(draft);data['examples']=data['examples'][2:]
    data['examples'][0]['content']=content
    report=preview(client,draft,data).json()
    assert report['status']=='invalid' and report['comparison']['status']=='notCompared',report
    assert rule in {finding['ruleId'] for finding in report['examples'][0]['results']},report


def custom(client,source,entries):
    response=client.post('/api/v1/profile-snapshots',json=source)
    assert response.status_code==201,response.text
    items=copy.deepcopy(sample(client)['distributions'])
    for item in items:
        item['profileSnapshotId']=None
        if item['type']=='jsonApi':item['api']['jsonSchemaArtifactId']=None;item['api']['openApiArtifactId']=None
        prefix='/credentialSubject' if item['type']=='w3cVc' else ''
        base=item['mapping']['entries'][0]
        item['mapping']['entries']=[base]+[base|entry|{'fieldPath':prefix+entry['fieldPath']} for entry in entries]
    return create(client,body()|{'profileSnapshotId':response.json()['id'],'distributions':items})


def test_nested_arrays_preserve_parent_correlation_and_unordered_multivalues(client):
    source=profile_input();source['entryShapeUris']=[P+'ProductShape']
    source['artifact']['content']+='''\n@prefix ex: <urn:example:> .
    demo:ProductShape sh:property [sh:path ex:addresses; sh:node ex:AddressShape; sh:class ex:Address; sh:minCount 1; sh:maxCount 3].
    ex:AddressShape a sh:NodeShape;
      sh:property [sh:path ex:zip; sh:datatype xsd:string; sh:minCount 1; sh:maxCount 1];
      sh:property [sh:path ex:city; sh:datatype xsd:string; sh:minCount 1; sh:maxCount 1].'''
    entries=[{'semanticPath':['urn:example:addresses'],'fieldPath':'/addresses/*','valueKind':'object','datatype':None,'classUri':'urn:example:Address','minCount':1,'maxCount':3},
        {'semanticPath':['urn:example:addresses','urn:example:zip'],'fieldPath':'/addresses/*/zip'},
        {'semanticPath':['urn:example:addresses','urn:example:city'],'fieldPath':'/addresses/*/city'}]
    draft=custom(client,source,entries)
    assert draft['distributionValidation']['status']=='conforms',draft['distributionValidation']
    data=payload(draft)
    for index,example in enumerate(data['examples']):
        obj=json.loads(example['content']);inner=obj['credentialSubject'] if index==1 else obj
        inner['addresses']=[{'zip':'00100','city':'A'},{'zip':'00200','city':'B'}][::(-1 if index==2 else 1)]
        example['content']=json.dumps(obj)
    report=preview(client,draft,data).json()
    assert report['status']=='conforms' and report['comparison']['status']=='sameGraph',report
    obj=json.loads(data['examples'][2]['content'])
    obj['addresses'][0]['city'],obj['addresses'][1]['city']=obj['addresses'][1]['city'],obj['addresses'][0]['city']
    data['examples'][2]['content']=json.dumps(obj)
    report=preview(client,draft,data).json()
    assert report['comparison']['status']=='differentGraphs',report
    obj['addresses'][1]['city']=None;data['examples'][2]['content']=json.dumps(obj)
    report=preview(client,draft,data).json()
    assert report['status']=='invalid' and report['comparison']['status']=='notCompared'


@pytest.mark.parametrize('datatype,value,valid',[
    ('boolean',True,True),('boolean',1,False),('integer',123,True),('integer','123',False),
    ('positiveInteger',0,False),('nonNegativeInteger',0,True),('decimal','1234567890.0123456789',True),
    ('decimal',0.1,False),('double',1.5,True),('date','2026-02-30',False),('date','2026-10-16',True),
    ('dateTime','2026-10-16T10:15:00Z',True),('dateTime','2026-10-16T10:15:00+14:60',False),('dateTime','2026-10-16T10:15:00+15:00',False),('dateTime','2026-10-16T10:15:00.1234567Z',False),('anyURI','urn:synthetic:record:1',True),('anyURI','relative',False),
    ('language','fi',False)])
def test_explicit_datatypes_without_guessing_or_decimal_precision_loss(client,datatype,value,valid):
    from apps.api.conversion import typed_literal,ConversionError
    if valid:
        term=typed_literal(value,XSD+datatype,'/value')
        assert str(term.datatype)==XSD+datatype
        if datatype=='decimal':assert str(term)==value
    else:
        with pytest.raises(ConversionError):typed_literal(value,XSD+datatype,'/value')


def test_duplicate_literals_and_unmapped_nested_fields_rejected(client):
    source=profile_input();source['artifact']['content']+='\n demo:ProductShape sh:property [sh:path demo:tag; sh:datatype xsd:string; sh:minCount 0; sh:maxCount 3].'
    draft=custom(client,source,[{'semanticPath':[P+'tag'],'fieldPath':'/tags/*','minCount':0,'maxCount':3}])
    data=payload(draft);data['examples']=data['examples'][2:]
    for value,rule in [(['A','A'],'RDF_VALUE_LOSS'),('A','JSON_ARRAY'),(['A']*4,'JSON_CARDINALITY')]:
        data['examples'][0]['content']=json.dumps({'company_name':'A','tags':value})
        row=preview(client,draft,data).json()['examples'][0]
        assert row['status']=='invalid' and row['results'][0]['ruleId']==rule,row


def test_json_schema_and_shacl_are_separate_and_both_enforced(client):
    draft=sample(client);data=payload(draft);data['examples']=data['examples'][:1]
    data['examples'][0]['content']='{"companyName":3}'
    row=preview(client,draft,data).json()['examples'][0]
    assert row['structureValidation']['status']=='invalid' and 'rdf' not in row
    source=profile_input();source['artifact']['content']+='\ndemo:NameShape sh:in ("Allowed").'
    draft=custom(client,source,[])
    data=payload(draft);data['examples']=data['examples'][2:]
    row=preview(client,draft,data).json()['examples'][0]
    assert row['status']=='invalid' and row['semanticValidation']['status']=='invalid',row
    assert row['semanticValidation']['results'][0]['ruleId'].endswith('InConstraintComponent')


def test_permissions_csrf_and_if_match_and_no_snapshot(client):
    draft=sample(client);url='/api/v1/drafts/'+draft['draftId']+'/conversion-preview';data=payload(draft)
    assert client.post(url,json=data).status_code==428
    assert preview(client,draft,**{'If-Match':'"stale"'}).status_code==412
    csrf=client.headers.pop('X-CSRF-Token')
    assert preview(client,draft).status_code==403
    client.headers['X-CSRF-Token']=csrf
    authenticate(client,'conversion-reader',[UUID(ORG)],role='reader')
    assert preview(client,draft).status_code in (403,404)
    authenticate(client,'conversion-stranger',[])
    assert preview(client,draft).status_code==404
    client.cookies.clear()
    assert preview(client,draft).status_code==401


def test_limits_unknown_distribution_and_legacy_draft(client):
    draft=sample(client);data=payload(draft)
    for bad in [dict(examples=[]),dict(examples=data['examples']+[data['examples'][0]]),dict(examples=[data['examples'][0]]*2),
                dict(examples=[data['examples'][0]|{'synthetic':False}]),dict(examples=[data['examples'][0]|{'content':'ä'*60000}]),
                dict(examples=[item|{'content':'a'*70000} for item in data['examples']])]:
        assert preview(client,draft,bad).status_code==422
    data['examples'][0]['distributionId']=str(uuid4())
    assert preview(client,draft,data).json()['status']=='invalid'
    old=create(client)
    assert preview(client,old,payload(draft)).status_code==422
    data=payload(draft);data['examples']=data['examples'][2:]
    data['examples'][0]['content']='{"company_name":'+('[0,'*22)+'0'+(']'*22)+'}'
    report=preview(client,draft,data).json()
    assert report['status']=='invalid' and report['examples'][0]['results'][0]['ruleId']=='JSON_RESOURCE_LIMIT',report


def test_old_published_content_untouched_and_preview_not_published_report(client):
    draft=sample(client);version=publish(client,draft)
    draft=sample(client)
    report=preview(client,draft).json()
    assert report['status']=='conforms',report
    assert client.get('/api/v1/products/'+DEMO+'/versions/1.0.0').json()==version
    assert 'conversionPreview' not in version
    assert preview(client,draft,payload(draft)|{'report':report}).status_code==422


def test_metadata_conflicts_and_non_tree_roots_not_silently_converted(client):
    source=profile_input();source['artifact']['content']+='\ndemo:ProductShape sh:targetClass demo:OtherCompany.'
    draft=custom(client,source,[])
    data=payload(draft);data['examples']=data['examples'][2:]
    report=preview(client,draft,data).json()
    assert report['status']=='invalid' and report['examples'][0]['results'][0]['ruleId']=='ROOT_UNSUPPORTED',report
    items=copy.deepcopy(sample(client)['distributions'])
    items[2]['mapping']['entries'][0]['datatype']=XSD+'boolean'
    for item in items:
        item['profileSnapshotId']=None
        if item['type']=='jsonApi':item['api']['jsonSchemaArtifactId']=None;item['api']['openApiArtifactId']=None
    response=client.post('/api/v1/profile-snapshots',json=profile_input())
    draft=create(client,body()|{'profileSnapshotId':response.json()['id'],'distributions':items})
    report=preview(client,draft).json()
    assert report['status']=='invalid' and report['metadataValidation']['status']=='invalid'
    assert report['examples']==[] and report['comparison']['status']=='notCompared'


def test_expensive_shacl_stops_worker_and_keeps_api_ready(client):
    source=profile_input();source['artifact']['content']+='\ndemo:NameShape sh:pattern "^(a+)+$".'
    draft=custom(client,source,[])
    data=payload(draft);data['examples']=data['examples'][2:]
    data['examples'][0]['content']=json.dumps({'company_name':'a'*10000+'!'})
    response=preview(client,draft,data)
    assert response.status_code==200,response.text
    report=response.json()
    assert report['status']=='error' and report['comparison']['status']=='notCompared',report
    assert report['results'][0]['ruleId']=='CONVERSION_RESOURCE_LIMIT'
    assert client.get('/health/ready').status_code==200
    assert client.get('/api/v1/products/'+draft['id']+'/draft').json()==draft
