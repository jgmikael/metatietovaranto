"""True JSON-LD processor, offline SHACL, package workflow and public artifact contracts."""
import copy
import hashlib
import json
from pathlib import Path
from uuid import UUID,uuid4

import pytest
from pyld import jsonld
from rdflib import Graph, RDF, SH, URIRef, XSD, OWL
from rdflib.compare import isomorphic
from sqlalchemy import select
from sqlalchemy.orm import Session

from conftest import authenticate
from helpers import ORG,body,create,profile_input,publish,change
from apps.api.main import engine
from apps.api.models import ProfileSnapshot,ProductVersion
from apps.api.profiles import ProfileInput,snapshot_manifest,checksum
from apps.api.technical_packages import (proposal,generate,PackageRequest,GenerationError,local_loader,
    BASE_CONTEXT,FIXTURES,normalize_rdf11,check_type_metadata)
from apps.api.semantic_validation import validation_report

P='https://example.org/metatietovaranto/demo/'
DEMO='00000000-0000-4000-8000-000000000004'


def request(**kw):
    return PackageRequest(rootShapeUri=P+'ProductShape',acceptRepresentation=True,replaceMappings=True,
        mappingVersion='1.1.0',exampleContent='{"companyName":"Synteettinen Esimerkki Oy"}',synthetic=True,
        acceptFormatPolicies=True,**kw).model_dump(mode='json')


def sample(client):return client.get('/api/v1/products/'+DEMO+'/draft').json()


def generate_api(client,draft,data=None):
    return client.post('/api/v1/drafts/'+draft['draftId']+'/technical-package',json=data or request(),headers={'If-Match':draft['etag']})


def ready(client,draft=None,data=None):
    response=generate_api(client,draft or sample(client),data)
    assert response.status_code==200,response.text
    result=response.json()
    assert result['generation']['status']=='ready',result
    return result['draft']


def artifact(package,name):return json.loads(package['artifacts'][name]['content'])


def unit_source(extra='',root=P+'ProductShape'):
    source=profile_input();source['entryShapeUris']=[root];source['artifact']['content']+='\n'+extra
    return snapshot_manifest(ProfileInput.model_validate(source))


def unit_body(manifest):
    from pydantic import TypeAdapter
    from apps.api.distribution_contracts import Distribution
    items=json.loads(Path('fixtures/distributions-demo.json').read_text())
    for item in items:
        item['profileSnapshotId']=None
        if item['type']=='jsonApi':item['api']['jsonSchemaArtifactId']=None;item['api']['openApiArtifactId']=None
        if item['type']=='sdJwtVc':item['sdJwt']['selectiveDisclosure']='always'
    items=[item.model_dump(mode='json') for item in TypeAdapter(list[Distribution]).validate_python(items)]
    return {'title':'Synteettinen testikuvaus','description':'Synteettinen sisältö','profileSnapshotId':str(uuid4()),'distributions':items}


def generated(manifest,example,**kw):
    return generate(manifest,checksum(manifest),unit_body(manifest),request()|{'exampleContent':json.dumps(example),**kw},'https://catalog.example.org')[0]


def test_deterministic_contents_actual_jsonld_processor_shacl_and_immutable_source():
    manifest=unit_source();before=copy.deepcopy(manifest);body_=unit_body(manifest)
    one,items=generate(manifest,checksum(manifest),body_,request(),'https://catalog.example.org')
    two,_=generate(manifest,checksum(manifest),body_,request(),'https://catalog.example.org')
    assert one==two and manifest==before
    assert one['validation']['jsonLdGraphComparison']=='isomorphic'
    assert one['standards']['sdJwtVc']=='draft-ietf-oauth-sd-jwt-vc-19'
    for record in one['artifacts'].values():assert hashlib.sha256(record['content'].encode()).hexdigest()==record['sha256']
    context=artifact(one,'context.jsonld');vc=artifact(one,'unsigned-vc-example.jsonld')
    assert vc['@context'][0]==BASE_CONTEXT and 'proof' not in vc and 'UNSIGNED' in vc['description']
    assert not {'type','id','credentialSubject','issuer'} & context['@context'].keys()
    loader=local_loader({vc['@context'][1]:context,BASE_CONTEXT:json.loads((FIXTURES/'credentials-v2.jsonld').read_text())})
    rdf=jsonld.to_rdf({'@context':vc['@context'][1],**vc['credentialSubject']},options={'documentLoader':loader,'format':'application/n-quads'})
    actual=Graph().parse(data=rdf,format='nt')
    expected=Graph().parse(data=f'[] a <{P}Company>; <{P}companyName> "Synteettinen Esimerkki Oy" .',format='turtle')
    assert isomorphic(normalize_rdf11(actual),normalize_rdf11(expected))
    assert validation_report(manifest,checksum(manifest),{'serialization':'turtle','content':actual.serialize(format='turtle'),'synthetic':True})['status']=='conforms'
    with pytest.raises(Exception):jsonld.expand({'@context':'https://evil.example/unknown'},options={'documentLoader':loader})
    metadata=artifact(one,'sd-jwt-type-metadata.json');check_type_metadata(metadata)
    assert metadata['claims'][0]['path']==['companyName'] and metadata['claims'][0]['sd']=='always'
    assert set(metadata)=={'vct','name','description','claims','x-mtv-profile','x-mtv-mapping','x-mtv-schema'}
    assert one['artifacts']['context.jsonld']['url'].startswith('https://catalog.example.org/id/technical-packages/')


def test_nested_unordered_multivalues_scoped_names_original_iris_and_disclosure_paths():
    manifest=unit_source('''@prefix ext: <https://external.example/vocab#> .
    demo:ProductShape sh:property [sh:path ext:addresses;sh:node ext:AddressShape;sh:class ext:Address;sh:minCount 1;sh:maxCount 3].
    ext:AddressShape a sh:NodeShape; sh:property [sh:path <https://iri.suomi.fi/model/test/companyName>;sh:datatype xsd:string;sh:minCount 1;sh:maxCount 1];
       sh:property [sh:path ext:tags;sh:datatype xsd:string;sh:minCount 1;sh:maxCount 4].''')
    package=generated(manifest,{'companyName':'Demo','addresses':[{'companyName':'Nested','tags':['A','B']},{'companyName':'Other','tags':['C']}]})
    context=artifact(package,'context.jsonld')['@context']
    assert context['companyName']['@id']==P+'companyName'
    nested=context['addresses']['@context']
    assert nested['companyName']['@id']=='https://iri.suomi.fi/model/test/companyName'
    assert nested['tags']['@container']=='@set'
    metadata=artifact(package,'sd-jwt-type-metadata.json')
    claims={json.dumps(row['path']):row for row in metadata['claims']}
    assert claims[json.dumps(['addresses',None,'tags',None])]['sd']=='always'
    assert claims[json.dumps(['addresses',None,'tags'])]['sd']=='never'
    assert claims[json.dumps(['addresses'])]['sd']=='never'
    assert package['validation']['shacl']=='conforms'


@pytest.mark.parametrize('datatype,value',[
    ('string','S'),('boolean',True),('integer',-2),('nonNegativeInteger',0),('positiveInteger',1),
    ('decimal','1234567890.0123456789'),('double',1.25),('date','2026-10-17'),
    ('dateTime','2026-10-17T13:00:00Z'),('anyURI','https://iri.suomi.fi/model/test/')])
def test_supported_literal_types_roundtrip_without_semantic_loss(datatype,value):
    # Replace, do not intersect two incompatible datatype constraints.
    source=profile_input();source['artifact']['content']=source['artifact']['content'].replace('sh:datatype xsd:string',f'sh:datatype xsd:{datatype}')
    manifest=snapshot_manifest(ProfileInput.model_validate(source))
    package=generated(manifest,{'companyName':value})
    assert package['validation']['status']=='conforms'


@pytest.mark.parametrize('extra,rule',[
    ('demo:ProductShape sh:targetClass demo:Other.','SHACL_AMBIGUOUS'),
    ('demo:NameShape sh:path [sh:inversePath demo:foo].','SHACL_AMBIGUOUS'),
    ('demo:NameShape sh:pattern "a".','SHACL_UNSUPPORTED'),
    ('demo:ProductShape sh:property [sh:path demo:self;sh:node demo:ProductShape].','RECURSION'),
    ('demo:NameShape sh:deactivated true.','SHACL_UNSUPPORTED'),
    ('demo:ProductShape sh:property [sh:path <https://external.example/companyName>;sh:datatype xsd:string].','NAME_COLLISION'),
    ('demo:ProductShape sh:property [sh:path demo:issuer;sh:datatype xsd:string].','RESERVED_NAME'),
    ('demo:ProductShape sh:property [sh:path demo:description;sh:datatype xsd:string].','RESERVED_NAME'),
    ('demo:ProductShape sh:property [sh:path demo:unknown].','OBJECT_AMBIGUOUS'),
    ('demo:ProductShape sh:property [sh:path demo:lang;sh:datatype <http://www.w3.org/1999/02/22-rdf-syntax-ns#langString>].','DATATYPE_UNSUPPORTED'),
])
def test_unsupported_ambiguous_and_reserved_structures_fail_explicitly(extra,rule):
    result=proposal(unit_source(extra),{'rootShapeUri':P+'ProductShape','names':[]})
    assert result['status']=='invalid' and result['results'][0]['ruleId']==rule,result


def test_explicit_names_precede_iri_names_translated_labels_do_not_change_them_and_collisions_reviewable():
    extra='''demo:NameShape <http://uri.suomi.fi/datamodel/ns/iow#localName> "legalName"; sh:name "Uusi suomenkielinen nimi".
    demo:ProductShape sh:property [sh:path <https://external.example/legalName>;sh:datatype xsd:string;sh:maxCount 1].'''
    manifest=unit_source(extra)
    result=proposal(manifest,{'rootShapeUri':P+'ProductShape','names':[]})
    assert result['status']=='invalid' and result['results'][0]['ruleId']=='NAME_COLLISION'
    result=proposal(manifest,{'rootShapeUri':P+'ProductShape','names':[{'semanticPath':['https://external.example/legalName'],'fieldName':'externalName'}]})
    assert result['status']=='proposed',result
    assert next(row for row in result['fields'] if row['mapping']['semanticPath']==[P+'companyName'])['name']=='legalName'


def test_api_rights_proposal_no_mutation_save_reopen_approval_invalidation_and_public_artifacts(client):
    draft=sample(client)
    url='/api/v1/drafts/'+draft['draftId']+'/technical-package'
    response=client.post(url+'/proposal',json={'rootShapeUri':P+'ProductShape'},headers={'If-Match':draft['etag']})
    assert response.status_code==200 and response.json()['status']=='proposed',response.text
    assert client.get('/api/v1/products/'+DEMO+'/draft').json()==draft
    package_draft=ready(client,draft);package=package_draft['technicalPackage']
    assert package_draft['status']=='draft' and package_draft['revision']==draft['revision']+1
    assert client.get('/api/v1/products/'+DEMO+'/draft').json()==package_draft
    assert client.get(package['artifacts']['context.jsonld']['url']).status_code==404
    old_snapshot=client.get('/api/v1/profile-snapshots/'+draft['profileSnapshotId']).json()
    version=publish(client,package_draft)
    assert version['technicalPackage']==package
    assert client.get('/api/v1/profile-snapshots/'+draft['profileSnapshotId']).json()['manifest']==old_snapshot['manifest']
    for name,record in package['artifacts'].items():
        response=client.get(record['url'])
        assert response.status_code==200,response.text
        assert response.content.decode()==record['content']
        assert response.headers['content-type'].startswith(record['mediaType'])
        assert response.headers['etag']=='"'+record['sha256']+'"'
        assert response.headers['x-content-type-options']=='nosniff'
    published_draft=sample(client)
    opened=client.post('/api/v1/products/'+DEMO+'/drafts',headers={'If-Match':published_draft['etag']}).json()
    # Regeneration is an editorial action and invalidates an existing approval even for equal bytes.
    second=ready(client,opened,request()|{'mappingVersion':'1.1.0'})
    assert second['technicalPackage']['artifacts']==package['artifacts']
    submitted=client.post(url.rsplit('/technical-package',1)[0]+'/submit',headers={'If-Match':second['etag']}).json()
    token=client.cookies.get('mtv_session');csrf=client.headers['X-CSRF-Token']
    authenticate(client,'test-reviewer',[UUID(ORG)],role='publisher')
    approved=client.post('/api/v1/drafts/'+second['draftId']+'/reviews',json={'decision':'approved','reason':'Paketin esitykset ja lähde tarkastettu','sourceReviewed':True},headers={'If-Match':submitted['etag']}).json()
    assert approved['status']=='approved'
    # Restore original editor session and regenerate.
    client.cookies.set('mtv_session',token);client.headers['X-CSRF-Token']=csrf
    regenerated=ready(client,approved,request()|{'mappingVersion':'1.1.0'})
    assert regenerated['status']=='draft'
    assert client.get('/api/v1/products/'+DEMO+'/versions/1.0.0').json()==version
    # Editing a bound field marks package stale; it cannot pass submission.
    payload={key:regenerated[key] for key in __import__('apps.api.contracts',fromlist=['ProductWrite']).ProductWrite.model_fields}
    payload['title']='Uusi nimi'
    changed=change(client,regenerated,payload)
    assert changed['technicalPackage']['status']=='needsRegeneration'
    assert any(row.get('ruleId')=='PACKAGE_NOT_READY' for row in changed['validationErrors'])
    assert client.post('/api/v1/drafts/'+changed['draftId']+'/submit',headers={'If-Match':changed['etag']}).status_code==422
    # Withdrawn state never removes published contexts.
    authenticate(client,'test-reviewer',[UUID(ORG)],role='publisher')
    life=client.get('/api/v1/products/'+DEMO+'/versions/1.0.0/lifecycle').json()
    response=client.post('/api/v1/products/'+DEMO+'/lifecycle-events',json={'version':'1.0.0','status':'withdrawn','reason':'Synteettisen testin palvelu poistettu'},headers={'If-Match':life['etag'],'Idempotency-Key':str(uuid4())})
    assert response.status_code==201,response.text
    client.cookies.clear()
    assert client.get(package['artifacts']['context.jsonld']['url']).status_code==200
    assert client.get('/id/technical-packages/'+package['packageId']+'/unknown.json').status_code==404


def test_csrf_etag_roles_and_failed_generation_preserves_draft(client):
    draft=sample(client)
    assert client.post('/api/v1/drafts/'+draft['draftId']+'/technical-package',json=request()).status_code==428
    assert generate_api(client,draft|{'etag':'"stale"'}).status_code==412
    csrf=client.headers.pop('X-CSRF-Token')
    assert generate_api(client,draft).status_code==403
    client.headers['X-CSRF-Token']=csrf
    bad=generate_api(client,draft,request()|{'replaceMappings':False}).json()
    assert bad['generation']['results'][0]['ruleId']=='MAPPING_REPLACEMENT'
    assert sample(client)==draft
    # Prevent client-supplied ready reports or packages.
    assert generate_api(client,draft,request()|{'technicalPackage':{'status':'ready'}}).status_code==422
    authenticate(client,'package-reader',[UUID(ORG)],role='reader')
    assert generate_api(client,draft).status_code in (403,404)
    authenticate(client,'package-reviewer',[UUID(ORG)],role='publisher')
    assert generate_api(client,draft).status_code in (403,404)
    authenticate(client,'package-stranger',[])
    assert generate_api(client,draft).status_code==404
    client.cookies.clear()
    assert generate_api(client,draft).status_code==401


def test_legacy_publication_has_no_package_and_does_not_change_after_generation(client):
    snapshot=client.post('/api/v1/profile-snapshots',json=profile_input()).json()
    draft=create(client,body()|{'profileSnapshotId':snapshot['id']})
    version=publish(client,draft)
    assert 'technicalPackage' not in version
    ready(client)
    assert client.get('/api/v1/products/'+version['id']+'/versions/1.0.0').json()==version


def test_original_upstream_tietomallit_fixture_unchanged_and_limitations_explicit():
    raw=Path('fixtures/tietomallit/fi-dcatap-upstream.ttl').read_bytes()
    provenance=json.loads(Path('fixtures/tietomallit/provenance.json').read_text())
    assert hashlib.sha256(raw).hexdigest()==provenance['sha256']
    source=profile_input();source['profileUri']='http://uri.suomi.fi/datamodel/ns/fi-dcatap'
    source['entryShapeUris']=['http://uri.suomi.fi/datamodel/ns/fi-dcatap#CatalogRecord']
    source['artifact']['content']=raw.decode()
    manifest=snapshot_manifest(ProfileInput.model_validate(source))
    result=proposal(manifest,{'rootShapeUri':source['entryShapeUris'][0],'names':[]})
    assert result['status']=='invalid' and result['results'][0]['ruleId']=='SHACL_UNSUPPORTED'
    assert 'shacl#in' in result['results'][0]['message']
    # Explicit separate derived test case: preserve source references and national/external IRIs.
    # Not presented as support of the complete original fixture or a verified live export.
    graph=Graph().parse(data=raw.decode(),format='turtle')
    shape=URIRef(source['entryShapeUris'][0]);prop=next(p for p in graph.objects(shape,SH.property) if graph.value(p,SH.path)==URIRef('http://purl.org/dc/terms/modified'))
    sub=Graph();sub.add((shape,RDF.type,SH.NodeShape));sub.add((shape,SH.targetClass,graph.value(shape,SH.targetClass)));sub.add((shape,SH.property,prop))
    for p in (RDF.type,SH.path,SH.datatype,SH.minCount,SH.maxCount):
        for value in graph.objects(prop,p):sub.add((prop,p,value))
    profile=URIRef(source['profileUri']);sub.add((profile,RDF.type,OWL.Ontology))
    source['artifact']['content']=sub.serialize(format='turtle')
    scoped=snapshot_manifest(ProfileInput.model_validate(source))
    package=generated(scoped,{'modified':'2026-10-17T12:00:00Z'},rootShapeUri=str(shape))
    assert artifact(package,'context.jsonld')['@context']['modified']['@id']=='http://purl.org/dc/terms/modified'


def test_multiple_locked_vocabularies_equivalence_provenance_and_no_owl_replacement():
    source=profile_input()
    source['vocabularyReferences']=[{'uri':'https://iri.suomi.fi/model/national/','location':'platform','version':'1.0'},
        {'uri':'https://external.example/vocab#','location':'external','version':'2026'}]
    owl='''@prefix owl: <http://www.w3.org/2002/07/owl#> .
    <https://example.org/metatietovaranto/demo/companyName> owl:equivalentProperty <https://external.example/vocab#label> .'''
    source['dependencyArtifacts']=[{'uri':'https://external.example/vocab#','artifact':{'serialization':'turtle','content':owl,'sourceUrl':'https://external.example/exports/2026.ttl'}}]
    manifest=snapshot_manifest(ProfileInput.model_validate(source))
    before=copy.deepcopy(manifest)
    package=generated(manifest,{'companyName':'Synthetic'})
    assert manifest==before
    assert artifact(package,'context.jsonld')['@context']['companyName']['@id']==P+'companyName'
    mapping=artifact(package,'semantic-mapping.json')
    assert mapping['sourceVocabularyReferences']==source['vocabularyReferences']
    assert manifest['dependencies'][0]['artifact']['content']==owl
    assert manifest['dependencies'][0]['artifact']['sourceUrl']=='https://external.example/exports/2026.ttl'
    assert mapping['dependencyChecksums'][0]['sha256']==hashlib.sha256(owl.encode()).hexdigest()


def test_missing_format_decisions_and_invalid_synthetic_content_never_ready():
    manifest=unit_source();body_=unit_body(manifest)
    for value in ('{}','{"companyName":13}','{"companyName":"A","unmapped":"B"}'):
        with pytest.raises(Exception):generate(manifest,checksum(manifest),body_,request()|{'exampleContent':value},'https://catalog.example.org')
    changed=copy.deepcopy(body_);changed['distributions'][2]['security']['algorithms']=[]
    with pytest.raises(GenerationError) as error:generate(manifest,checksum(manifest),changed,request(),'https://catalog.example.org')
    assert error.value.finding['ruleId']=='FORMAT_POLICY_REQUIRED'
    changed=copy.deepcopy(body_);changed['distributions'][2]['sdJwt']['selectiveDisclosure']='perClaim';changed['distributions'][2]['mapping']['entries']=[]
    with pytest.raises(GenerationError) as error:generate(manifest,checksum(manifest),changed,request(),'https://catalog.example.org')
    assert error.value.finding['ruleId']=='DISCLOSURE_REQUIRED'


def test_explicit_selected_root_does_not_mutate_multi_root_snapshot(client):
    source=profile_input();source['artifact']['content']+='''
    demo:OtherShape a sh:NodeShape;sh:targetClass demo:Other;
      sh:property [sh:path demo:otherValue;sh:datatype xsd:string;sh:minCount 1;sh:maxCount 1].'''
    response=client.post('/api/v1/profile-snapshots',json=source);assert response.status_code==201,response.text
    snap=response.json();items=copy.deepcopy(sample(client)['distributions'])
    for item in items:
        item['profileSnapshotId']=None
        if item['type']=='jsonApi':item['api']['jsonSchemaArtifactId']=None;item['api']['openApiArtifactId']=None
    draft=create(client,body()|{'profileSnapshotId':snap['id'],'distributions':items})
    package_draft=ready(client,draft)
    assert not package_draft['validationErrors'],package_draft['validationErrors']
    assert package_draft['semanticValidation']['selectedRootShapeUri']==P+'ProductShape'
    assert package_draft['distributionValidation']['selectedRootShapeUri']==P+'ProductShape'
    stored=client.get('/api/v1/profile-snapshots/'+snap['id']).json()
    assert stored['manifest']['entryShapeUris']==[]
    examples=[{'distributionId':item['id'],'synthetic':True,'content':json.dumps({'credentialSubject':{'companyName':'Synthetic'}} if item['type']=='w3cVc' else {'companyName':'Synthetic'})} for item in package_draft['distributions']]
    response=client.post('/api/v1/drafts/'+draft['draftId']+'/conversion-preview',json={'examples':examples},headers={'If-Match':package_draft['etag']})
    assert response.json()['status']=='conforms',response.text
    assert response.json()['selectedRootShapeUri']==P+'ProductShape'
    assert publish(client,package_draft)['technicalPackage']['rootShapeUri']==P+'ProductShape'


def test_unresolved_source_and_invalid_metadata_cannot_be_ready():
    manifest=unit_source();manifest['issues']=['Lukittu riippuvuus puuttuu']
    with pytest.raises(GenerationError) as error:generated(manifest,{'companyName':'Synthetic'})
    assert error.value.finding['ruleId']=='SOURCE_NOT_READY'
    for doc in [dict(vct='urn:test',claims=[{'path':'/wrong','sd':'always','mandatory':True}]),
                dict(vct='urn:test',claims=[{'path':['a'],'sd':'unknown','mandatory':True}]),
                dict(vct='urn:test',claims=[],schema_uri='https://not-a-standard-field.example')]:
        with pytest.raises(GenerationError):check_type_metadata(doc)


def test_generation_cannot_bypass_provider_editor_membership(client):
    draft=sample(client)
    orgs=client.get('/api/v1/organizations').json()['items']
    other=next(org['id'] for org in orgs if org['id']!=ORG)
    from apps.api.contracts import ProductWrite
    payload={key:draft[key] for key in ProductWrite.model_fields};payload['providerOrganizationId']=other
    changed=change(client,draft,payload)
    authenticate(client,'owner-without-provider-edit',[UUID(ORG)],role='editor')
    assert client.get('/api/v1/products/'+DEMO+'/draft').status_code==200
    assert generate_api(client,changed).status_code in (403,404)


def test_non_disclosable_policy_paths_cannot_be_lost_by_field_renaming():
    manifest=unit_source();data=unit_body(manifest)
    data['distributions'][2]['sdJwt']['nonDisclosableClaims'].append('/company_name')
    with pytest.raises(GenerationError) as error:generate(manifest,checksum(manifest),data,request(),'https://catalog.example.org')
    assert error.value.finding['ruleId']=='DISCLOSURE_PATH_REVIEW'


def test_generation_and_proposal_respect_current_private_profile_read_permission(client):
    draft=sample(client);other=next(org['id'] for org in client.get('/api/v1/organizations').json()['items'] if org['id']!=ORG)
    from apps.api.contracts import ProductWrite
    payload={key:draft[key] for key in ProductWrite.model_fields};payload['providerOrganizationId']=other
    created=create(client,payload)
    authenticate(client,'editor-without-source-profile',[UUID(other)],role='editor')
    assert client.get('/api/v1/products/'+created['id']+'/draft').status_code==200
    assert client.get('/api/v1/profile-snapshots/'+created['profileSnapshotId']).status_code==404
    assert generate_api(client,created).status_code==404
    response=client.post('/api/v1/drafts/'+created['draftId']+'/technical-package/proposal',json={'rootShapeUri':P+'ProductShape'},headers={'If-Match':created['etag']})
    assert response.status_code==404
