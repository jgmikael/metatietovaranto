"""Metadata reader and integrity checker, not an SD-JWT/signature verifier. Stdlib only."""
import base64
import hashlib
import json

MAX_BYTES=2_000_000

def integrity(raw):
    return 'sha256-'+base64.b64encode(hashlib.sha256(raw).digest()).decode('ascii')


def checked_json(raw, expected):
    if len(raw)>MAX_BYTES or not expected.startswith('sha256-'):
        raise ValueError('Unsupported integrity algorithm or document size')
    try:digest=base64.b64decode(expected[7:],validate=True)
    except Exception:raise ValueError('Invalid base64 integrity') from None
    if len(digest)!=32 or hashlib.sha256(raw).digest()!=digest:raise ValueError('Integrity mismatch')
    def unique(pairs):
        value={}
        for key,item in pairs:
            if key in value:raise ValueError('Duplicate JSON member')
            value[key]=item
        return value
    return json.loads(raw,object_pairs_hook=unique)


def claim_path(pointer):
    return [None if p=='*' else p.replace('~1','/').replace('~0','~') for p in pointer[1:].split('/')]


def resolve_claim(raw, expected_integrity, selected_path, load):
    """No claim values required. `load` supplies only explicitly allowed documents."""
    doc=checked_json(raw,expected_integrity)
    descriptor=doc['x-mtv-profile']
    profile=checked_json(load(descriptor['uri']),descriptor['integrity'])
    if descriptor['version']!='1.0.0' or profile['version']!=descriptor['version']:
        raise ValueError('Unsupported semantic extension version')
    mapping_ref=doc['x-mtv-mapping']
    mapping=checked_json(load(mapping_ref['uri']),mapping_ref['integrity'])
    matches=[row for row in doc['claims'] if row['path']==selected_path]
    if len(matches)!=1:raise ValueError('Claim path is missing or ambiguous in descriptions')
    semantic=matches[0]['x-mtv-semantic']
    rows=[row for row in mapping['attributes'] if row['claimPath']==semantic['claimPath']]
    if len(rows)!=1 or rows[0]!=semantic:raise ValueError('Conflicting semantic annotation/mapping')
    # The array container has the same semantic constraint as its elements, explicitly marked.
    if selected_path!=semantic['claimPath'] and not (semantic['claimPath'][-1] is None and selected_path==semantic['claimPath'][:-1]):
        raise ValueError('Claim path does not match semantic context')
    if semantic['term']!=semantic['semanticPath'][-1]:raise ValueError('Conflicting property IRI')
    return {'propertyIri':semantic['term'],'shacl':semantic['shacl'],'rootShapeUri':semantic['rootShapeUri'],
            'semanticPath':semantic['semanticPath'],'sourceProfile':semantic['sourceProfile'],
            'scope':'description lookup only; no presentation completeness or signature validation'}


def verify_bundle(raw, expected_integrity, load):
    """Additional structure/annotation consistency; never interpret a partial presentation."""
    doc=checked_json(raw,expected_integrity)
    schema_ref=doc['x-mtv-schema'];schema=checked_json(load(schema_ref['uri']),schema_ref['integrity'])
    mapping_ref=doc['x-mtv-mapping'];mapping=checked_json(load(mapping_ref['uri']),mapping_ref['integrity'])
    if schema['x-mtv-profile']!=doc['x-mtv-profile'] or mapping['extensionProfile']!=doc['x-mtv-profile'] or schema['x-mtv-mapping']!=mapping_ref:
        raise ValueError('Conflicting extension/mapping reference')
    for row in mapping['attributes']:
        node=schema
        parts=row['fieldPath'][1:].split('/')
        for index,part in enumerate(parts):
            if part=='*':node=node['items']
            else:
                node=node['properties'][part.replace('~1','/').replace('~0','~')]
                # Annotation is on the property/array, not a fabricated item PropertyShape.
                if index==len(parts)-1 or index==len(parts)-2 and parts[-1]=='*':
                    if node.get('x-term')!=row['term'] or node.get('x-mtv-shacl')!=row:
                        raise ValueError('Conflicting JSON Schema semantic annotation')
        resolve_claim(raw,expected_integrity,row['claimPath'],load)
    return True
