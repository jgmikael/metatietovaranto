"""Generate local synthetic review packages, without a DB, HTTP or publication."""
import argparse,hashlib,json
from pathlib import Path
from uuid import uuid5,NAMESPACE_URL
from rdflib import Graph
from rdflib.compare import to_isomorphic
from pydantic import TypeAdapter
from apps.api.distribution_contracts import Distribution
from apps.api.profiles import checksum
from apps.api.technical_packages import generate,PackageRequest
ROOT=Path(__file__).resolve().parents[1]
P='https://example.org/representation/'

def example_package(kind):
    content=(ROOT/'fixtures/representations'/f'{kind}.ttl').read_text()
    manifest={'profileUri':P+'profile','sourceVersion':'synthetic-1','sourceArtifacts':[{'id':str(uuid5(NAMESPACE_URL,P+kind)),
        'name':kind+'.ttl','content':content,'serialization':'turtle','sha256':hashlib.sha256(content.encode()).hexdigest()}],
        'derivedArtifacts':[],'dependencies':[],'issues':[],'entryShapeUris':[P+'Root'],'vocabularyReferences':[],
        'graphHash':str(to_isomorphic(Graph().parse(data=content,format='turtle')).internal_hash())}
    profile_hash=checksum(manifest);snapshot_id=str(uuid5(NAMESPACE_URL,profile_hash))
    items=json.loads((ROOT/'fixtures/distributions-demo.json').read_text())
    for d in items:
        d['profileSnapshotId']=snapshot_id;d['mapping']['entries']=[]
        if d['type']=='jsonApi':d['api']['jsonSchemaArtifactId']=None;d['api']['openApiArtifactId']=None
        if d['type']=='sdJwtVc':d['sdJwt']['selectiveDisclosure']='always'
    adapter=TypeAdapter(list[Distribution]);items=adapter.dump_python(adapter.validate_python(items),mode='json')
    choices={'languageRepresentation':'valueLanguage-v1'} if kind=='language' else {'references':[[P+'parent']]}
    request=PackageRequest(rootShapeUri=P+'Root',acceptRepresentation=True,replaceMappings=True,
        mappingVersion='1.0.0',exampleContent=(ROOT/'fixtures/representations'/f'{kind}.json').read_text(),
        synthetic=True,acceptFormatPolicies=True,**choices).model_dump(mode='json')
    return generate(manifest,profile_hash,{'profileSnapshotId':snapshot_id,'title':'Synthetic '+kind,
        'description':'Local unsigned implementation example; planned URLs are not published','distributions':items},request,'https://planned.example.org')[0]

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    for kind in ['language','reference']:
        package=example_package(kind);directory=args.output/kind;directory.mkdir(parents=True,exist_ok=True)
        for name,artifact in package['artifacts'].items():(directory/name).write_text(artifact['content'],encoding='utf-8')
        print(json.dumps({'example':kind,'status':package['status'],'packageId':package['packageId'],'jsonLd':package['validation']['jsonLdGraphComparison'],'shacl':package['validation']['shacl'],'publication':'not published'}))
