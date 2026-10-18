"""SHACL-derived MTV semantic extension 1.0.0; no independent content model."""
import copy
import json
from pathlib import Path
from apps.api.profiles import canonical
from apps.semantic_reader import integrity,claim_path,verify_bundle

VERSION='1.0.0'
SOURCES=Path(__file__).resolve().parents[2]/'fixtures/catalog-standards'


def source_pins():return json.loads((SOURCES/'sources.json').read_text())


def profile_definition(uri):
    return {'id':uri,'version':VERSION,'name':'Metatietovaranto semantic annotations',
        'status':'local extension; no ETSI/EUDI conformance claim',
        'keywords':{'x-term':'Original OWL/RDF property IRI, never a JSON Schema $ref',
            'x-mtv-shacl':'Complete attribute reference including root, constraintPath and frozen source snapshot',
            'x-mtv-semantic':'Same complete reference in each Type Metadata claim',
            'x-mtv-profile':'Extension version, definition URI and sha256 SRI integrity',
            'x-mtv-schema':'Explicit local schema discovery: URI and sha256 SRI; not standard schema/schema_uri',
            'x-mtv-mapping':'Versioned mapping URI and sha256 SRI'},
        'constraintLocator':{'root':'rootShapeUri','steps':'sh:property with the direct propertyPath; then sh:node or unique sh:targetClass selection',
            'blankNodes':'No original URI claimed. null propertyShapeUri/nodeShapeUri + snapshot and constraintPath identify the occurrence.',
            'ambiguity':'Multiple properties for a step or multiple candidate node shapes are rejected.'},
        'claimPaths':'IETF draft-ietf-oauth-sd-jwt-vc-19 arrays of strings/null, not JSON Pointer wildcards',
        'arrayContainers':'Same property constraint; container path removes final null; claim semantic reference retains full element path.',
        'unknownExtensions':'Standard consumers may ignore x-* members. No assumption that wallets interpret these semantics.',
        'validationScope':'Full issuance content uses schema and SHACL. Missing disclosures in a presentation do not prove absence in the original credential.',
        'integrity':'sha256- plus standard base64 of exact UTF-8 octets; never hexadecimal or base64url',
        'trust':'Integrity is not issuer authentication, a signature check or catalogue registration.'}


def attach_references(tree, snapshot_id, snapshot_hash, manifest, base_url):
    source={'uri':manifest['profileUri'],'version':manifest.get('sourceVersion'),'snapshotId':snapshot_id,
            'snapshotSha256':snapshot_hash,'snapshotUrl':base_url+'/api/v1/profile-snapshots/'+snapshot_id}
    refs=[]
    def visit(node):
        for row in node['fields']:
            entry=row['mapping']
            ref={'rootShapeUri':entry['shapeUri'],'semanticPath':entry['semanticPath'],
                 'term':entry['semanticPath'][-1],'fieldPath':entry['fieldPath'],
                 'claimPath':claim_path(entry['fieldPath']),'sourceProfile':copy.deepcopy(source),'shacl':row['shacl']}
            row['semantic']=ref;refs.append(ref)
            if 'child' in row:visit(row['child'])
    visit(tree)
    return refs


def catalogue_report(refs, external):
    valid={(r['rootShapeUri'],tuple(r['semanticPath'])) for r in refs}
    for reference in external:
        if reference['kind']=='attribute' and (reference['rootShapeUri'],tuple(reference['semanticPath'])) not in valid:
            raise ValueError('Catalogue correspondence refers to an unknown SHACL occurrence')
    return {'status':'partial','conformanceClaim':False,'sources':source_pins(),
        'references':external,'coverage':[
            {'target':'TS11.Attribute.identifier','local':'sourceProfile + term; optional attribute catalogue reference','status':'partial','missing':'authoritative catalogue-assigned identifier'},
            {'target':'TS11.Attribute.semanticDataSpecification','local':'SHACL sourceProfile snapshotUrl/URI/checksum','status':'described'},
            {'target':'TS11.Attribute.distributions','local':'x-mtv-schema URI + integrity','status':'localExtension'},
            {'target':'TS11.Attribute.name/description','local':'source labels and product descriptions','status':'partial','missing':'verified English attribute descriptions'},
            {'target':'TS11.Attribute.contactInfo/legalBasis','local':None,'status':'missing'},
            {'target':'TS11.Attribute.authenticSources','local':'distribution responsible organizations','status':'partial','missing':'authoritative Member State/source IDs and verification endpoint'},
            {'target':'TS11.SchemaMeta.id/version/rulebookURI','local':'packageId and optional scheme reference','status':'partial','missing':'catalogue ID and reviewed Rulebook with scheme version'},
            {'target':'TS11.SchemaMeta.trustedAuthorities/attestationLoS','local':None,'status':'missing'},
            {'target':'TS11.SchemaMeta.bindingType','local':'distribution holderBinding declaration','status':'partial','missing':'reviewed mapping to scheme bindingType; no automatic key/claim/biometric inference'},
            {'target':'TS11.SchemaMeta.supportedFormats/schemaURIs','local':'distribution type and package artifact URLs','status':'described'},
        ],'missing':[
            {'code':'NORMATIVE_SOURCES_UNVERIFIED','detail':'ETSI V1.2.1/V1.1.1 and current consolidated EU 2025/1569 amendments unavailable (403)'},
            {'code':'CATALOGUE_REGISTRATION_NOT_IMPLEMENTED','detail':'No authoritative Attribute/Scheme catalogue registration or approval implied'},
            {'code':'AUTHENTIC_SOURCE_VERIFICATION_NOT_IMPLEMENTED','detail':'Verification endpoints, legal authority and trust approval require the external issuer/catalogue process'},
        ]+([{'code':'SOURCE_VERSION_UNDECLARED','detail':'Source profile has no declared version; frozen snapshot checksum remains explicit'}] if any(r['sourceProfile']['version'] is None for r in refs) else [])+
        ([{'code':'CATALOGUE_REFERENCES_UNDECLARED','detail':'No approved external catalogue correspondences supplied'}] if not external else [])}


def enrich(prefix, tree, refs, schema, metadata, mapping, external):
    """Acyclic octet chain: profile -> mapping -> schema -> Type Metadata -> issuer pin."""
    profile=profile_definition(prefix+'semantic-extension-profile.json')
    profile_raw=canonical(profile).encode()
    descriptor={'version':VERSION,'uri':profile['id'],'integrity':integrity(profile_raw)}
    mapping.update({'extensionProfile':descriptor,'attributes':refs,'catalogueReferences':external})
    mapping_raw=canonical(mapping).encode()
    mapping_ref={'uri':prefix+'semantic-mapping.json','integrity':integrity(mapping_raw)}
    schema.update({'x-mtv-profile':descriptor,'x-mtv-mapping':mapping_ref})
    schema_raw=canonical(schema).encode()
    schema_ref={'uri':prefix+'content.schema.json','integrity':integrity(schema_raw)}
    metadata.update({'x-mtv-profile':descriptor,'x-mtv-mapping':mapping_ref,'x-mtv-schema':schema_ref})
    by_path={canonical(r['claimPath']):r for r in refs}
    for claim in metadata['claims']:
        ref=by_path.get(canonical(claim['path']))
        if ref is None:ref=by_path.get(canonical(claim['path']+[None]))
        if ref is None:raise ValueError('Unknown claim in semantic extension')
        claim['x-mtv-semantic']=copy.deepcopy(ref)
    metadata_raw=canonical(metadata).encode()
    docs={descriptor['uri']:profile_raw,mapping_ref['uri']:mapping_raw,schema_ref['uri']:schema_raw}
    verify_bundle(metadata_raw,integrity(metadata_raw),docs.__getitem__)
    validate_against_source(refs,schema,metadata,mapping)
    binding={'vct':metadata['vct'],'vct#integrity':integrity(metadata_raw),
        'typeMetadataUri':prefix+'sd-jwt-type-metadata.json','scope':'public metadata pin for the external issuer; not a credential or signature',
        'discovery':'For HTTPS vct the issuer must serve these exact metadata bytes at vct or use the selected standard retrieval mechanism; URN vct requires an agreed metadata discovery mechanism.'}
    return profile,binding,catalogue_report(refs,external)


def validate_against_source(refs,schema,metadata,mapping):
    """`refs` must be freshly derived from the locked SHACL, never client annotations."""
    if mapping['attributes']!=refs:raise ValueError('Mapping conflicts with frozen SHACL')
    expected={canonical(r['claimPath']):r for r in refs}
    for claim in metadata['claims']:
        ref=expected.get(canonical(claim['path'])) or expected.get(canonical(claim['path']+[None]))
        if ref is None or claim.get('x-mtv-semantic')!=ref:raise ValueError('Type Metadata conflicts with frozen SHACL')
    for ref in refs:
        node=schema;parts=ref['fieldPath'][1:].split('/')
        if parts[-1]=='*':parts=parts[:-1]
        for i,part in enumerate(parts):
            node=node['items'] if part=='*' else node['properties'][part]
            if i==len(parts)-1:
                if node.get('x-term')!=ref['term'] or node.get('x-mtv-shacl')!=ref:
                    raise ValueError('JSON Schema conflicts with frozen SHACL')
