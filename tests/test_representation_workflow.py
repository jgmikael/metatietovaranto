"""New representations use the existing authenticated publication workflow."""
import json
from pathlib import Path
from uuid import UUID
import pytest
from conftest import authenticate
from helpers import ORG,profile_input,change,publish
from apps.api.contracts import ProductWrite
from test_technical_packages import sample,request,generate_api
P='https://example.org/representation/'

@pytest.mark.parametrize('kind',['language','reference'])
def test_new_representation_publication_and_approval_invalidation(client,kind):
    text=Path('fixtures/representations/'+kind+'.ttl').read_text()
    if kind=='language':
        content={'labels':[{'value':'Hei','language':'fi'},{'value':'Hej','language':'sv'}]}
        rdf='[] a <'+P+'Record>; <'+P+'labels> "Hei"@fi,"Hej"@sv .'
        choices={'languageRepresentation':'valueLanguage-v1'}
    else:
        content={'parent':['https://synthetic.example/entities/parent']}
        rdf='[] a <'+P+'Entity>; <'+P+'parent> <https://synthetic.example/entities/parent> . <https://synthetic.example/entities/parent> a <'+P+'Entity> .'
        choices={'references':[[P+'parent']]}
    source=profile_input();source.update(profileUri=P+'profile',sourceVersion='synthetic-1',entryShapeUris=[P+'Root'])
    source['artifact']['content']=text
    source['vocabularyReferences']=[{'uri':P,'location':'external'}]
    imported=client.post('/api/v1/profile-snapshots',json=source);assert imported.status_code==201,imported.text
    snapshot=imported.json();draft=sample(client)
    payload={key:draft[key] for key in ProductWrite.model_fields};payload['profileSnapshotId']=snapshot['id'];payload['derivedExamples']=[];payload['syntheticExample']={'serialization':'turtle','synthetic':True,'content':rdf}
    for d in payload['distributions']:
        d['profileSnapshotId']=snapshot['id'];d['mapping']['entries']=[]
        if d['type']=='jsonApi':d['api']['jsonSchemaArtifactId']=None;d['api']['openApiArtifactId']=None
        if d['type']=='sdJwtVc':d['sdJwt']['selectiveDisclosure']='always'
    draft=change(client,draft,payload)
    data=request()|{'rootShapeUri':P+'Root','exampleContent':json.dumps(content),**choices}
    response=generate_api(client,draft,data);assert response.status_code==200,response.text
    assert response.json()['generation']['status']=='ready',response.text
    ready=response.json()['draft'];assert client.get('/api/v1/products/'+ready['id']+'/draft').json()==ready
    version=publish(client,ready);package=version['technicalPackage']
    for record in package['artifacts'].values():assert client.get(record['url']).content.decode()==record['content']
    reopened=client.post('/api/v1/products/'+ready['id']+'/drafts',headers={'If-Match':client.get('/api/v1/products/'+ready['id']+'/draft').json()['etag']}).json()
    regenerated=generate_api(client,reopened,data).json()['draft']
    submitted=client.post('/api/v1/drafts/'+regenerated['draftId']+'/submit',headers={'If-Match':regenerated['etag']}).json()
    token=client.cookies.get('mtv_session');csrf=client.headers['X-CSRF-Token']
    authenticate(client,'representation-reviewer',[UUID(ORG)],role='publisher')
    approved=client.post('/api/v1/drafts/'+submitted['draftId']+'/reviews',json={'decision':'approved','reason':'Synteettinen kieli-/viittausprofiili tarkastettu','sourceReviewed':True},headers={'If-Match':submitted['etag']}).json();assert approved['status']=='approved'
    client.cookies.set('mtv_session',token);client.headers['X-CSRF-Token']=csrf
    again=generate_api(client,approved,data);assert again.status_code==200,again.text
    assert again.json()['draft']['status']=='draft'
    assert client.get('/api/v1/products/'+ready['id']+'/versions/1.0.0').json()==version
