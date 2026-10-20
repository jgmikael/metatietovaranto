"""Server-derived assertions for the *actual browser worker*, without any DB or API."""
import hashlib,json
from pathlib import Path
from pydantic import TypeAdapter
from apps.api.distribution_contracts import Distribution
from apps.api.profiles import canonical,checksum
from apps.api.technical_packages import inspect_profile,context_for,schema_for,generate
from apps.api.semantic_extension import attach_references
ROOT=Path(__file__).resolve().parents[1]

def reference():
    content=(ROOT/'fixtures/browser-generation/tree.ttl').read_text()
    profile_uri='https://iri.suomi.fi/model/mtv-browser-test/profile'
    file={'name':'tree.ttl','content':content,'sha256':hashlib.sha256(content.encode()).hexdigest()}
    profile_hash=checksum({'profileUri':profile_uri,'sourceVersion':'synthetic-1','sources':[{'sha256':file['sha256']}]})
    profile_id=profile_hash[:8]+'-'+profile_hash[8:12]+'-5'+profile_hash[13:16]+'-a'+profile_hash[17:20]+'-'+profile_hash[20:32]
    manifest={'profileUri':profile_uri,'sourceVersion':'synthetic-1','sourceArtifacts':[file|{'id':'00000000-0000-4000-8000-000000000001','serialization':'turtle'}],
      'derivedArtifacts':[],'dependencies':[],'issues':[],'graphHash':'0'*64,'entryShapeUris':[profile_uri.rsplit('/',1)[0]+'/PersonShape'],'vocabularyReferences':[]}
    root=manifest['entryShapeUris'][0]
    tree,rows=inspect_profile(manifest,root,[])
    refs=attach_references(tree,profile_id,profile_hash,manifest,'https://planned.example.org')
    for ref in refs:ref['sourceProfile']['snapshotUrl']=None
    distributions=json.loads((ROOT/'fixtures/distributions-demo.json').read_text())
    for d in distributions:
        d['profileSnapshotId']=profile_id
        d['mapping']['entries']=[]
        if d['type']=='sdJwtVc':d['sdJwt']['selectiveDisclosure']='always'
    settings={'profileId':profile_id,'rootShapeUri':root,'names':[],'mappingVersion':'1.0.0',
        'publicationBase':'https://planned.example.org','exampleContent':(ROOT/'fixtures/browser-generation/example.json').read_text(),
        'acceptRepresentation':True,'acceptFormatPolicies':True,'synthetic':True}
    distributions=TypeAdapter(list[Distribution]).dump_python(TypeAdapter(list[Distribution]).validate_python(distributions),mode='json')
    metadata={'title':'Synteettinen selainvertailu','description':'No issuance','distributions':distributions,'profileSnapshotId':profile_id}
    body=metadata|{'profileSnapshotId':profile_id}
    request=settings|{'replaceMappings':True}
    package,_=generate(manifest,profile_hash,body,request,'https://planned.example.org')
    claims=json.loads(package['artifacts']['sd-jwt-type-metadata.json']['content'])['claims']
    for claim in claims:
        claim['x-mtv-semantic']['sourceProfile']['snapshotUrl']=None
    return {'profile':{'id':profile_id,'profileUri':profile_uri,'sourceVersion':'synthetic-1','sha256':profile_hash,'sources':[file]},
      'settings':settings,'metadata':metadata,'expected':{'context':{'@context':context_for(tree)},'schema':{'$schema':'https://json-schema.org/draft/2020-12/schema',**schema_for(tree)},
      'rows':[{k:row[k] for k in ('name','nameOrigin','mapping','multi','labels','shacl')} for row in rows],'claims':claims}}
if __name__=='__main__':print(canonical(reference()))
