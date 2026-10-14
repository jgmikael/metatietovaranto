import json
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5, uuid4, UUID
from sqlalchemy.orm import Session
from apps.api.main import engine
from apps.api.models import Organization, OrganizationMembership
from conftest import authenticate

ID='00000000-0000-4000-8000-000000000001'
ORG=str(uuid5(NAMESPACE_URL,f'https://example.org/metatietovaranto/legacy-provider/{ID}'))

def body():
    data=json.loads(Path('fixtures/products.json').read_text())[0]
    return {k:v for k,v in data.items() if k not in ('id','provider','dataElements')}|{'providerOrganizationId':ORG}

def profile_input():
    return {'organizationId':ORG,'profileUri':'https://example.org/metatietovaranto/demo/profile',
        'sourceDeclaration':'Synteettinen testifixture; ei oikea Tietomallit-export. Käytetään vain ohjelmistotestissä.',
        'sourceVersion':'demo-1','ingestionMethod':'upload',
        'artifact':{'serialization':'turtle','content':Path('fixtures/semantic-profile-demo.ttl').read_text()},
        'vocabularyReferences':[{'uri':'https://example.org/metatietovaranto/demo/','location':'external'}]}

def import_profile(client):
    response=client.post('/api/v1/profile-snapshots',json=profile_input())
    assert response.status_code==201,response.text
    return response.json()

def create(client,data=None):
    response=client.post('/api/v1/products',json=data or body(),headers={'Idempotency-Key':str(uuid4())})
    assert response.status_code==201,response.text
    return response.json()

def change(client,draft,data):
    response=client.put('/api/v1/products/'+draft['id'],json=data,headers={'If-Match':draft['etag']})
    assert response.status_code==200,response.text
    return response.json()

def publish(client,draft,version='1.0.0'):
    original_cookie=client.cookies.get('mtv_session');original_csrf=client.headers.get('X-CSRF-Token')
    response=client.post(f"/api/v1/drafts/{draft['draftId']}/submit",headers={'If-Match':draft['etag']})
    assert response.status_code==200,response.text
    draft=response.json()
    authenticate(client,'test-reviewer',[UUID(ORG)],role='publisher')
    response=client.post(f"/api/v1/drafts/{draft['draftId']}/reviews",json={'decision':'approved','reason':'Synteettisen testifixturen lähde ja graafi tarkastettu','sourceReviewed':True},headers={'If-Match':draft['etag']})
    assert response.status_code==200,response.text
    approved=response.json()
    response=client.post(f"/api/v1/drafts/{draft['draftId']}/publish",json={'version':version},
        headers={'If-Match':approved['etag'],'Idempotency-Key':str(uuid4())})
    assert response.status_code==200,response.text
    client.cookies.set('mtv_session',original_cookie);client.headers['X-CSRF-Token']=original_csrf
    return response.json()
