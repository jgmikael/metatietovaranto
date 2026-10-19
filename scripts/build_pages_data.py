"""Build only allowlisted repository fixtures. Never import main, connect to DB or export a DB.
Run: uv run python -m scripts.build_pages_data
"""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit
from uuid import NAMESPACE_URL,uuid5

from apps.api.contracts import ProductWrite
from apps.api.metadata_exports import product_jsonld
from apps.api.profiles import ProfileInput,snapshot_manifest,checksum,canonical
from apps.api.technical_packages import PackageRequest,generate
from apps.api.distributions import assess
from apps.api.semantic_validation import validation_report

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_BASE='https://jgmikael.github.io/metatietovaranto'


def build(output:Path,public_base=DEFAULT_BASE):
    public_base=public_base.rstrip('/')
    url=urlsplit(public_base)
    if url.scheme!='https' or not url.hostname or url.username or url.password or url.query or url.fragment or url.path!='/metatietovaranto':
        raise ValueError('Pages base must be an HTTPS origin with /metatietovaranto path, no credentials/query/fragment')
    spec=json.loads((ROOT/'fixtures/pages/demo.json').read_text())
    resources={};files={}
    def save(path,content):
        if not isinstance(content,str):content=canonical(content)
        files[path]=content.encode('utf-8')
    def export(logical,path,content):resources[logical]=path;save(path,content)
    organizations=[];products=[]
    legacy=json.loads((ROOT/'fixtures/products.json').read_text())
    for index,fixture in enumerate(legacy):
        org_id='57c5e449-303c-5387-a2a4-050308cefaff' if index==0 else str(uuid5(NAMESPACE_URL,'pages-org:'+fixture['id']))
        organizations.append({'id':org_id,'legalName':fixture['provider'],'country':'FI','synthetic':True,'identifiers':[{'scheme':'synthetic-demo','value':fixture['id']}]})
        data={key:value for key,value in fixture.items() if key not in {'id','provider','dataElements'}}
        body=ProductWrite(**data,providerOrganizationId=org_id).model_dump(mode='json')
        products.append(body|{'id':fixture['id'],'provider':fixture['provider'],'dataElements':fixture['dataElements']})
    org=organizations[0]
    manifest=snapshot_manifest(ProfileInput.model_validate({'organizationId':org['id'],
        'profileUri':'https://example.org/metatietovaranto/demo/profile','sourceVersion':'synthetic-demo-2e',
        'ingestionMethod':'upload','sourceDeclaration':'Synteettinen ohjelmistofixture; ei oikea Tietomallit-export tai rekisteriote.',
        'vocabularyReferences':[{'uri':'https://example.org/metatietovaranto/demo/','location':'external'}],
        'artifact':{'serialization':'turtle','content':(ROOT/'fixtures/semantic-profile-demo.ttl').read_text()}}))
    # Only a newly created synthetic build snapshot: remove run-time metadata before hashing.
    # Real application snapshots and source RDF bytes are never modified.
    for source in manifest['sourceArtifacts']:
        old=source['id'];source['id']=str(uuid5(NAMESPACE_URL,'pages-artifact:'+source['sha256']))
        source.pop('acquiredAt',None)
        if manifest['shapesArtifactId']==old:manifest['shapesArtifactId']=source['id']
    profile_hash=checksum(manifest);snapshot_id=str(uuid5(NAMESPACE_URL,'pages-snapshot:'+profile_hash))
    snapshot_path=f'demo/profiles/{snapshot_id}.json'
    summary={'id':snapshot_id,'profileId':str(uuid5(NAMESPACE_URL,manifest['profileUri'])),'sha256':profile_hash,**{key:manifest[key] for key in ['profileUri','sourceVersion','verificationStatus','sourceDeclaration','issues','elements']}}
    snapshot=summary|{'manifest':manifest}
    save(snapshot_path,snapshot)
    for source in manifest['sourceArtifacts']:
        export(f'/api/v1/profile-snapshots/{snapshot_id}/artifacts/{source["id"]}',f'demo/profiles/{snapshot_id}/source.ttl',source['content'])
    definitions=json.loads((ROOT/'fixtures/distributions-demo.json').read_text())
    for definition in definitions:
        definition['profileSnapshotId']=snapshot_id
        if definition['type']=='sdJwtVc':definition['sdJwt']['selectiveDisclosure']='always'
    comprehensive=spec['comprehensiveProduct']
    body=ProductWrite(**{key:value for key,value in comprehensive.items() if key!='id'},providerOrganizationId=org['id'],
        profileSnapshotId=snapshot_id,distributions=definitions,
        syntheticExample={'serialization':'turtle','content':(ROOT/'fixtures/semantic-example-demo.ttl').read_text(),'synthetic':True}).model_dump(mode='json')
    request=PackageRequest(**spec['representation'],exampleContent=(ROOT/'fixtures/derived-example-demo.json').read_text()).model_dump(mode='json')
    package,distributions=generate(manifest,profile_hash,body,request,public_base,snapshot_url=public_base+'/'+snapshot_path)
    body.update(distributions=distributions,primaryDistributionId=next(item['id'] for item in distributions if item['type']=='w3cVc'))
    # Validate the final display body using the same typed write contract.
    body=ProductWrite.model_validate(body).model_dump(mode='json')
    semantic_report=validation_report(manifest,profile_hash,body['syntheticExample'])
    semantic_report.pop('checkedAt',None)  # Run time is not part of the static fixture's deterministic content.
    products.append(body|{'id':comprehensive['id'],'provider':org['legalName'],'dataElements':manifest['elements'],
        'profileSnapshot':summary,'semanticProfileSnapshot':summary,'technicalPackage':package,
        'semanticValidation':semantic_report,
        'distributionValidation':assess(manifest,distributions)})
    for name,artifact in package['artifacts'].items():
        path=urlsplit(artifact['url']).path.removeprefix('/metatietovaranto/')
        save(path,artifact['content'])
        assert hashlib.sha256(files[path]).hexdigest()==artifact['sha256']
    for organization in organizations:
        save('id/organizations/'+organization['id'],{'@context':{'dct':'http://purl.org/dc/terms/'},'@id':public_base+'/id/organizations/'+organization['id'],'@type':'dct:Agent','dct:title':organization['legalName'],'synthetic':True})
    for product in products:
        product.update(version=spec['version'],modifiedAt=spec['snapshotDate'],status='published',
            uri=public_base+'/#'+product['id'],versionUri=public_base+'/#'+product['id']+'@'+spec['version'])
        product['contentHash']=checksum(product)
        lifecycle={'productId':product['id'],'version':spec['version'],'sequence':1,'status':'published','revision':0,
            'etag':'"'+product['contentHash']+'"','versionContentHash':product['contentHash'],'reason':None,'replacementVersion':None,'replacementVersionUri':None,'events':[],
            'uri':public_base+'/demo/products/'+product['id']+'/lifecycle.json'}
        product['lifecycle']=lifecycle
        export(f'/api/v1/products/{product["id"]}/export?format=json&version={spec["version"]}',f'demo/products/{product["id"]}/metadata.json',product)
        export(f'/api/v1/products/{product["id"]}/export?format=jsonld&version={spec["version"]}',f'demo/products/{product["id"]}/metadata.jsonld',product_jsonld(product,public_base))
        save(f'demo/products/{product["id"]}/lifecycle.json',lifecycle)
    export('/api/v1/catalog/export?format=json','demo/exports/catalog.json',{'items':products})
    export('/api/v1/catalog/export?format=jsonld','demo/exports/catalog.jsonld',{'@context':{'dcat':'http://www.w3.org/ns/dcat#'},'@type':'dcat:Catalog','dcat:dataset':[product_jsonld(product,public_base) for product in products]})
    save('demo/catalog.json',{'version':spec['version'],'synthetic':True,'publicBase':public_base,'items':products,'organizations':organizations,'profiles':[snapshot],'resources':resources})
    save('.nojekyll','')
    # Exact allowlist and digest inventory; the workflow uploads only Vite dist-pages.
    save('demo/inventory.json',{'publicBase':public_base,'synthetic':True,'files':{name:hashlib.sha256(raw).hexdigest() for name,raw in sorted(files.items())}})
    output=Path(output)
    if output.is_symlink():raise ValueError('Symlink output directory is not allowed')
    output.mkdir(parents=True,exist_ok=True)
    # Remove only previously generated allowlisted files, never an arbitrary output directory.
    inventory=output/'demo/inventory.json'
    previous=json.loads(inventory.read_text())['files'] if inventory.exists() else {}
    allowed=set(previous)|set(files)
    for path in output.rglob('*'):
        if path.is_symlink():raise ValueError('Symlink in generated data directory: '+str(path))
        if path.is_file() and path.relative_to(output).as_posix() not in allowed:
            raise ValueError('Unexpected file in generated data directory: '+str(path))
    for name in previous:
        path=output/name
        if not path.resolve().is_relative_to(output.resolve()):raise ValueError('Invalid inventory path')
        if path.is_file():path.unlink()
    for name,raw in files.items():
        path=output/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
    return files


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=ROOT/'.pages-data');parser.add_argument('--public-base',default=DEFAULT_BASE)
    args=parser.parse_args();files=build(args.output,args.public_base);print(f'Built {len(files)} static files from repository synthetic fixtures; no database or identity service used.')
