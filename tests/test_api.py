from uuid import uuid4
from pathlib import Path
from rdflib import Graph,URIRef,Literal
from rdflib.namespace import RDF,DCAT,DCTERMS
from sqlalchemy.orm import Session
from sqlalchemy import select
from apps.api.main import engine
from apps.api.models import Product
from helpers import body,create,change,import_profile,publish,ID,ORG


def test_seed_health_and_private_legacy_data(client):
    assert client.get('/health/ready').json()=={'status':'ready','database':'postgresql'}
    assert client.get('/api/v1/products').json()['total']==0
    items=client.get('/api/v1/my/products').json()['items']
    assert len(items)==4 and all(item['status']=='draft' for item in items)
    legacy=[item for item in items if item['id']!='00000000-0000-4000-8000-000000000004']
    assert len(legacy)==3 and all(item['profileSnapshotId'] is None for item in legacy)
    assert all(item['validationErrors'] for item in legacy)


def test_private_crud_etag_and_persistence(client):
    draft=create(client)
    with Session(engine) as session:
        assert session.get(Product,draft['id']) is not None
    assert client.get('/api/v1/products/'+draft['id']).status_code==404
    assert client.get('/api/v1/products/'+draft['id']+'/draft').json()['title']==draft['title']
    data=body()|{'title':'Muokattu tuote'}
    assert client.put('/api/v1/products/'+draft['id'],json=data).status_code==428
    updated=change(client,draft,data)
    assert client.put('/api/v1/products/'+draft['id'],json=data,headers={'If-Match':draft['etag']}).status_code==412
    assert updated['title']==data['title']
    assert client.delete('/api/v1/products/'+draft['id'],headers={'If-Match':updated['etag']}).status_code==204
    assert client.get('/api/v1/products/'+draft['id']+'/draft').status_code==404


def test_validation_and_create_idempotency(client):
    for field in ('title','description','theme','source','purpose','limitations','accessConditions'):
        assert client.post('/api/v1/products',json=body()|{field:'  '}).status_code==422
    assert client.post('/api/v1/products',json=body()|{'dataElements':[{'name':'Rinnakkainen malli'}]}).status_code==422
    key=str(uuid4());headers={'Idempotency-Key':key}
    first=client.post('/api/v1/products',json=body(),headers=headers)
    assert first.status_code==201
    assert client.post('/api/v1/products',json=body(),headers=headers).json()==first.json()
    assert client.post('/api/v1/products',json=body()|{'title':'Toinen'},headers=headers).status_code==409


def test_public_search_exports_and_versions(client):
    profile=import_profile(client)
    published=[]
    for title,theme in [('Verovelkatieto','Verotus'),('Yrityksen tiedot','Yritykset')]:
        draft=create(client,body()|{'title':title,'theme':theme,'profileSnapshotId':profile['id']})
        published.append(publish(client,draft))
    assert client.get('/api/v1/products').json()['total']==2
    assert client.get('/api/v1/products?q=VEROVELKA&theme=Verotus').json()['total']==1
    assert client.get('/api/v1/products?q=%25').json()['total']==0
    page=client.get('/api/v1/products?limit=1&offset=1').json()
    assert len(page['items'])==1 and page['total']==2
    assert client.get('/api/v1/products?limit=101').status_code==422
    item=published[0];product_id=item['id']
    assert client.get(f'/api/v1/products/{product_id}/export').json()==item
    graph=Graph().parse(data=client.get(f'/api/v1/products/{product_id}/export?format=jsonld').text,format='json-ld')
    assert (URIRef(item['versionUri']),RDF.type,DCAT.Dataset) in graph
    assert (URIRef(item['versionUri']),DCTERMS.title,Literal(item['title'],lang='fi')) in graph
    assert len(client.get('/api/v1/catalog/export').json()['items'])==2
    assert len(list(Graph().parse(data=client.get('/api/v1/catalog/export?format=jsonld').text,format='json-ld').subjects(RDF.type,DCAT.Dataset)))==2
    version=client.get(f'/api/v1/products/{product_id}/versions/1.0.0')
    assert version.json()==item and version.headers['etag']=='"'+item['contentHash']+'"'
    assert client.get(f'/id/products/{product_id}',headers={'Accept':'application/ld+json'}).headers['vary']=='Accept'
    assert client.get(f'/id/products/{product_id}',follow_redirects=False).status_code==303


def test_organization_api(client):
    organizations=client.get('/api/v1/organizations').json()['items']
    assert len(organizations)==3
    for organization in organizations:
        assert client.get('/api/v1/organizations/'+organization['id']).json()==organization
    assert client.get('/api/v1/organizations/'+str(uuid4())).status_code==404
