"""Semantic occurrences, extension consistency and exact-octet integrity, not JWT verification."""
import copy,json
from pathlib import Path
from uuid import UUID,uuid4

import pytest
from rdflib import URIRef,SH
from apps.api.profiles import checksum,canonical
from apps.api.semantic_validation import locked_graph
from apps.api.semantic_extension import validate_against_source,source_pins
from apps.semantic_reader import integrity,checked_json,resolve_claim,verify_bundle
from test_technical_packages import unit_source,unit_body,generated,request,artifact,ready,sample,DEMO,P
from helpers import body,create,change,publish,ORG
from apps.api.contracts import ProductWrite


def documents(package):return {record['url']:record['content'].encode() for record in package['artifacts'].values()}

def metadata_raw(package):return package['artifacts']['sd-jwt-type-metadata.json']['content'].encode()


def test_one_attribute_agrees_with_source_schema_metadata_and_named_property_shape():
    source=unit_source();package=generated(source,{'companyName':'Synthetic'})
    schema=artifact(package,'content.schema.json');meta=artifact(package,'sd-jwt-type-metadata.json');mapping=artifact(package,'semantic-mapping.json')
    ref=meta['claims'][0]['x-mtv-semantic'];assert ref==mapping['attributes'][0]==schema['properties']['companyName']['x-mtv-shacl']
    assert schema['properties']['companyName']['x-term']==ref['term']==P+'companyName'
    assert ref['shacl']['propertyShapeUri']==P+'NameShape' and ref['term']!=ref['shacl']['propertyShapeUri']
    assert ref['shacl']['nodeShapeUri']==P+'ProductShape'
    graph=locked_graph(source);assert graph.value(URIRef(ref['shacl']['propertyShapeUri']),SH.path)==URIRef(ref['term'])
    assert ref['sourceProfile']['version']=='demo-1' and ref['sourceProfile']['snapshotSha256']==checksum(source)
    assert 'schema' not in meta and 'schema_uri' not in meta
    assert verify_bundle(metadata_raw(package),integrity(metadata_raw(package)),documents(package).__getitem__)
    assert checked_json(package['artifacts']['semantic-extension-profile.json']['content'].encode(),meta['x-mtv-profile']['integrity'])['version']=='1.0.0'


def nested_source():
    return unit_source('''@prefix e: <https://external.example/vocab#> .
    demo:ProductShape sh:property [sh:path e:home;sh:node e:Home;sh:class e:HomeAddress;sh:minCount 1;sh:maxCount 1];
      sh:property [sh:path e:work;sh:node e:Work;sh:class e:WorkAddress;sh:minCount 1;sh:maxCount 1].
    e:Home a sh:NodeShape;sh:property [sh:path <https://one.example/city>;sh:datatype xsd:string;sh:minCount 1;sh:maxCount 1].
    e:Work a sh:NodeShape;sh:property [sh:path <https://two.example/city>;sh:datatype xsd:string;sh:minCount 1;sh:maxCount 1].''')


def test_same_field_names_in_different_roles_and_blank_property_shapes():
    source=nested_source();package=generated(source,{'companyName':'S','home':{'city':'A'},'work':{'city':'B'}})
    raw=metadata_raw(package);docs=documents(package)
    # Resolver reads no schema or example/claim values, only Type Metadata, extension and mapping.
    calls=[]
    def load(url):
        calls.append(url)
        assert url.rsplit('/',1)[-1] not in ('content.schema.json','content-example.json','sd-jwt-claims-example.json')
        return docs[url]
    home=resolve_claim(raw,integrity(raw),['home','city'],load)
    work=resolve_claim(raw,integrity(raw),['work','city'],load)
    assert home['propertyIri']=='https://one.example/city' and work['propertyIri']=='https://two.example/city'
    assert home['semanticPath']!=work['semanticPath']
    assert home['shacl']['nodeShapeUri']=='https://external.example/vocab#Home'
    assert home['shacl']['propertyShapeKind']=='blankNode' and home['shacl']['propertyShapeUri'] is None
    assert len(home['shacl']['constraintPath'])==2
    assert home['shacl']['constraintPath'][0]['propertyPath']=='https://external.example/vocab#home'
    assert '_:' not in canonical(home['shacl'])
    assert verify_bundle(raw,integrity(raw),docs.__getitem__)


def test_nested_arrays_convert_wildcards_to_null_and_keep_constraint_path():
    source=unit_source('''@prefix e: <https://external.example/vocab#> .
    demo:ProductShape sh:property [sh:path e:groups;sh:node e:Group;sh:class e:GroupClass;sh:minCount 1;sh:maxCount 3].
    e:Group a sh:NodeShape;sh:property [sh:path e:members;sh:node e:Member;sh:class e:MemberClass;sh:minCount 1;sh:maxCount 3].
    e:Member a sh:NodeShape;sh:property [sh:path e:city;sh:datatype xsd:string;sh:minCount 1;sh:maxCount 1].''')
    package=generated(source,{'companyName':'S','groups':[{'members':[{'city':'A'}]}]})
    raw=metadata_raw(package);result=resolve_claim(raw,integrity(raw),['groups',None,'members',None,'city'],documents(package).__getitem__)
    assert len(result['semanticPath'])==3 and len(result['shacl']['constraintPath'])==3
    paths=[row['path'] for row in artifact(package,'sd-jwt-type-metadata.json')['claims']]
    assert ['groups',None,'members',None,'city'] in paths
    assert all('*' not in path for path in paths)
    assert resolve_claim(raw,integrity(raw),['groups'],documents(package).__getitem__)['propertyIri'].endswith('#groups')


@pytest.mark.parametrize('target',['schemaTerm','schemaShape','mapping','metadata'])
def test_conflicting_annotations_rejected_against_frozen_source(target):
    package=generated(unit_source(),{'companyName':'S'})
    schema=artifact(package,'content.schema.json');meta=artifact(package,'sd-jwt-type-metadata.json');mapping=artifact(package,'semantic-mapping.json')
    refs=copy.deepcopy(mapping['attributes'])
    if target=='schemaTerm':schema['properties']['companyName']['x-term']='https://wrong.example/property'
    elif target=='schemaShape':schema['properties']['companyName']['x-mtv-shacl']['shacl']['propertyShapeUri']='https://wrong.example/shape'
    elif target=='mapping':mapping['attributes'][0]['term']='https://wrong.example/property'
    else:meta['claims'][0]['x-mtv-semantic']['semanticPath']=['https://wrong.example/path']
    with pytest.raises(ValueError):validate_against_source(refs,schema,meta,mapping)


@pytest.mark.parametrize('target',['semantic-extension-profile.json','content.schema.json','semantic-mapping.json','sd-jwt-type-metadata.json'])
def test_every_integrity_link_detects_changed_octets_including_semantically_identical_json(target):
    package=generated(unit_source(),{'companyName':'S'});docs=documents(package);raw=metadata_raw(package)
    record=package['artifacts'][target];docs[record['url']]+=b' '
    if target=='sd-jwt-type-metadata.json':raw+=b' '
    with pytest.raises(ValueError,match='Integrity'):verify_bundle(raw,integrity(metadata_raw(package)),docs.__getitem__)


def test_standard_sri_not_hex_or_base64url_and_not_an_authenticity_claim():
    import base64,hashlib
    raw=b'published exact octets'
    assert integrity(raw)=='sha256-'+base64.b64encode(hashlib.sha256(raw).digest()).decode()
    with pytest.raises(ValueError):checked_json(b'{}','sha256-'+hashlib.sha256(b'{}').hexdigest())
    package=generated(unit_source(),{'companyName':'S'})
    binding=artifact(package,'issuer-metadata-binding.json')
    assert binding['vct#integrity']==integrity(metadata_raw(package))
    assert 'not a credential or signature' in binding['scope']


def reference():
    return {'kind':'attribute','catalogueUri':'https://catalogue.example/attributes','entryUri':'https://catalogue.example/attributes/company-name/1',
            'version':'1','relation':'related','rootShapeUri':P+'ProductShape','semanticPath':[P+'companyName'],
            'provenance':{'sourceUri':'https://catalogue.example/decisions/123','sourceVersion':'2026-10-18',
                          'evidenceSha256':'a'*64,'statement':'Synthetic reviewed correspondence declaration, not an automatic equivalence.'}}


def test_catalogue_references_persist_reopen_invalidate_approval_and_publish_immutably(client):
    first=ready(client);version=publish(client,first)
    published=sample(client)
    opened=client.post('/api/v1/products/'+DEMO+'/drafts',headers={'If-Match':published['etag']}).json()
    payload={key:opened[key] for key in ProductWrite.model_fields};payload['catalogueReferences']=[reference()]
    changed=change(client,opened,payload)
    assert changed['technicalPackage']['status']=='needsRegeneration'
    assert sample(client)['catalogueReferences']==[reference()]
    # Older clients omitting the new optional field cannot silently delete references.
    payload.pop('catalogueReferences');changed=change(client,changed,payload)
    assert changed['catalogueReferences']==[reference()]
    regenerated=ready(client,changed,request()|{'mappingVersion':'1.1.0'})
    assert artifact(regenerated['technicalPackage'],'semantic-mapping.json')['catalogueReferences']==[reference()]
    assert client.get('/api/v1/products/'+DEMO+'/versions/1.0.0').json()==version
    next_version=publish(client,regenerated,'1.1.0')
    for name in ('semantic-extension-profile.json','issuer-metadata-binding.json','catalogue-coverage.json'):
        rec=next_version['technicalPackage']['artifacts'][name];response=client.get(rec['url'])
        assert response.status_code==200 and response.content.decode()==rec['content']
    report=artifact(next_version['technicalPackage'],'catalogue-coverage.json')
    assert report['status']=='partial' and not report['conformanceClaim']


def test_invalid_catalogue_correspondence_or_missing_provenance_rejected(client):
    draft=sample(client);payload={key:draft[key] for key in ProductWrite.model_fields}
    payload['catalogueReferences']=[reference()];payload['catalogueReferences'][0]['provenance'].pop('evidenceSha256')
    response=client.put('/api/v1/products/'+DEMO,json=payload,headers={'If-Match':draft['etag']})
    assert response.status_code==422
    payload['catalogueReferences']=[reference()|{'semanticPath':['https://unknown.example/field']}]
    changed=change(client,draft,payload)
    response=client.post('/api/v1/drafts/'+draft['draftId']+'/technical-package',json=request(),headers={'If-Match':changed['etag']})
    assert response.json()['generation']['status']=='invalid'


def test_pinned_ts11_source_checksums_and_unverified_normative_versions_explicit():
    pins=source_pins();root=Path('fixtures/catalog-standards')
    import hashlib
    for name,digest in pins['ts11']['files'].items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest
    assert pins['ts11']['version'].startswith('1.0.1')
    assert len(pins['requestedUnverifiedSources'])==1
    assert pins['euConsolidation']['currentAsOfReviewDate'] is None


def test_webcor_projection_annotations_preserve_source_iris_without_claiming_original_profile_version():
    from test_technical_packages import webcor_source,WEBCOR,EU_CORE
    from apps.api.profiles import ProfileInput,snapshot_manifest
    source=snapshot_manifest(ProfileInput.model_validate(webcor_source(projected=True)))
    package=generated(source,{'familyName':['Synteettinen Testiperhe']},rootShapeUri=WEBCOR+'Person')
    schema=artifact(package,'content.schema.json');metadata=artifact(package,'sd-jwt-type-metadata.json')
    ref=next(claim['x-mtv-semantic'] for claim in metadata['claims'] if claim['path']==['familyName',None])
    assert schema['properties']['familyName']['x-term']==ref['term']==EU_CORE+'familyName'
    assert schema['properties']['familyName']['x-mtv-shacl']==ref
    assert ref['shacl']['propertyShapeUri']==WEBCOR+'familyName' and ref['shacl']['nodeShapeUri']==WEBCOR+'Person'
    assert ref['sourceProfile']['uri']=='urn:metatietovaranto:test:webcor-family-name'
    assert ref['sourceProfile']['version']=='0.0.2-local-test-1' and ref['sourceProfile']['snapshotSha256']==checksum(source)
    raw=metadata_raw(package)
    assert resolve_claim(raw,integrity(raw),['familyName',None],documents(package).__getitem__)['propertyIri']==EU_CORE+'familyName'


def test_reviewed_normative_copies_are_pinned_without_claiming_later_amendments_absent():
    import hashlib
    pins=source_pins();root=Path('fixtures/catalog-standards')
    assert len(pins['reviewedProvidedCopies'])==3
    for item in pins['reviewedProvidedCopies']:
        raw=(root/item['file']).read_bytes()
        assert raw.startswith(b'%PDF-') and len(raw)==item['byteLength']
        assert hashlib.sha256(raw).hexdigest()==item['sha256']
        assert item['reviewedClauses'] and 'User-uploaded copy' in item['provenance']
    assert pins['euConsolidation']['date']=='2026-08-11'
    assert pins['euConsolidation']['listedAmendingAct'].startswith('EU 2026/1735')
    assert pins['euConsolidation']['currentAsOfReviewDate'] is None


def test_generated_coverage_distinguishes_reviewed_texts_currentness_and_issuer_profile():
    package=generated(unit_source(),{'companyName':'S'})
    report=artifact(package,'catalogue-coverage.json')
    codes={row['code'] for row in report['missing']}
    assert 'NORMATIVE_SOURCES_UNVERIFIED' not in codes
    assert {'EU_CORRIGENDUM_STATUS_UNVERIFIED','ETSI_SD_JWT_PROFILE_VERSION_DIFFERENCE','EXTERNAL_ISSUER_PROFILE_NOT_VERIFIED'}<=codes
    assert report['status']=='partial' and not report['conformanceClaim']
    assert any(row['target'].startswith('EU2025/1569 Article7(5)') for row in report['coverage'])
    assert any(row['target'].startswith('EU2025/1569 Article8(3)') for row in report['coverage'])
    evidence=report['sources']['documentInformationEvidence']
    assert evidence['observations']['latestDisplayedConsolidation']=='2026-08-11'
    assert report['sources']['euConsolidation']['latestDisplayedVersionConfirmed'] is True
    assert report['sources']['euConsolidation']['currentAsOfReviewDate'] is None
    assert not evidence['observations']['separateCorrigendumRegisterDisplayed']
    assert package['generator']=='technical-package/1.1.1'
    assert package['standards']['sdJwtVc']=='draft-ietf-oauth-sd-jwt-vc-19'


def test_document_information_evidence_is_pinned_without_inferring_corrigendum_absence():
    import hashlib
    pins=source_pins();evidence=pins['documentInformationEvidence']
    raw=(Path('fixtures/catalog-standards')/evidence['file']).read_bytes()
    assert raw.startswith(b'%PDF-') and len(raw)==evidence['byteLength']
    assert hashlib.sha256(raw).hexdigest()==evidence['sha256']
    assert evidence['observations']['relationshipSectionBasicAct']=='32025R1569'
    assert pins['euConsolidation']['latestDisplayedVersionConfirmed'] is True
    assert pins['euConsolidation']['currentAsOfReviewDate'] is None
    assert any(row['code']=='EU_CORRIGENDUM_STATUS_UNVERIFIED' for row in pins['remainingReviewGaps'])
    assert 'CELEX:32025R1569' in pins['requestedUnverifiedSources'][0]['url']
