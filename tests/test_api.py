import json
from pathlib import Path
from uuid import uuid4

from rdflib import Graph, URIRef, Literal
from rdflib.namespace import DCTERMS, RDF, DCAT
from sqlalchemy import select
from sqlalchemy.orm import Session
from apps.api.main import engine, Product

FIXTURES = json.loads(Path('fixtures/products.json').read_text())
ID = FIXTURES[0]['id']

def payload():
    return json.loads(json.dumps({k:v for k,v in FIXTURES[0].items() if k != 'id'}))

def test_seed_and_health(client):
    assert client.get('/health/ready').json() == {'status':'ready','database':'postgresql'}
    items=client.get('/api/v1/products').json()['items']
    assert len(items)==3
    assert all(p['synthetic'] and p['demo'] for p in items)

def test_search_filters_pagination(client):
    assert client.get('/api/v1/products',params={'q':'VEROVELKA'}).json()['total']==1
    assert client.get('/api/v1/products',params={'theme':'Pätevyydet'}).json()['total']==1
    assert client.get('/api/v1/products',params={'provider':'Demo-yritysrekisteri'}).json()['total']==1
    assert client.get('/api/v1/products',params={'q':'ei-osumia'}).json()['items']==[]
    assert client.get('/api/v1/products',params={'q':'%'}).json()['total']==0
    one=client.get('/api/v1/products',params={'limit':1}).json()
    two=client.get('/api/v1/products',params={'limit':1,'offset':1}).json()
    assert one['total']==3 and one['items'][0]['id']!=two['items'][0]['id']
    assert client.get('/api/v1/products?limit=101').status_code==422

def test_crud_persistence(client):
    data=payload();data['title']='Uusi synteettinen tuote'
    response=client.post('/api/v1/products',json=data)
    assert response.status_code==201
    product_id=response.json()['id']
    assert response.headers['location']==f'/api/v1/products/{product_id}'
    # Verify persisted through a separate database connection, not only the HTTP response.
    with Session(engine) as session:
        assert session.scalar(select(Product).where(Product.title==data['title'])) is not None
    data['title']='Muokattu tuote'
    assert client.put(f'/api/v1/products/{product_id}',json=data).json()['title']==data['title']
    assert client.get(f'/api/v1/products/{product_id}').json()['title']==data['title']
    assert client.delete(f'/api/v1/products/{product_id}').status_code==204
    assert client.get(f'/api/v1/products/{product_id}').status_code==404

def test_validation(client):
    for field in ('title','description','provider','theme','source','purpose','limitations','accessConditions'):
        data=payload();data[field]='  '
        assert client.post('/api/v1/products',json=data).status_code==422
    for field,value in [('synthetic',False),('dataElements',[]),('availability','production'),('title','x'*201)]:
        data=payload();data[field]=value
        assert client.post('/api/v1/products',json=data).status_code==422
    data=payload();data['dataElements'][0]['semanticUri']='javascript:alert(1)'
    assert client.post('/api/v1/products',json=data).status_code==422
    assert client.put(f'/api/v1/products/{uuid4()}',json=payload()).status_code==404
    assert client.get('/api/v1/products/not-a-uuid').status_code==422
    data=payload();data['dataElements'][0]['name']='  '
    assert client.post('/api/v1/products',json=data).status_code==422

def test_json_exports_and_rdf_meaning(client):
    normal=client.get(f'/api/v1/products/{ID}').json()
    assert client.get(f'/api/v1/products/{ID}/export?format=json').json()==normal
    exported=client.get(f'/api/v1/products/{ID}/export?format=jsonld')
    assert exported.headers['content-type']=='application/ld+json'
    graph=Graph().parse(data=exported.text,format='json-ld')
    subject=URIRef(normal['uri'])
    assert (subject,RDF.type,DCAT.Dataset) in graph
    assert (subject,DCTERMS.title,Literal(normal['title'],lang='fi')) in graph
    for element in normal['dataElements']:
        assert list(graph.triples((None,DCTERMS.conformsTo,URIRef(element['semanticUri']))))
    catalog=client.get('/api/v1/catalog/export?format=jsonld')
    catalog_graph=Graph().parse(data=catalog.text,format='json-ld')
    assert len(list(catalog_graph.subjects(RDF.type,DCAT.Dataset)))==3
    assert len(client.get('/api/v1/catalog/export?format=json').json()['items'])==3
    assert client.get(f'/api/v1/products/{ID}/export?format=turtle').status_code==422

def test_uri_negotiation_and_missing(client):
    for accept in ('application/json','application/ld+json'):
        response=client.get(f'/id/products/{ID}',headers={'Accept':accept})
        assert response.status_code==200 and response.headers['vary']=='Accept'
        assert response.headers['content-type']==accept
    html=client.get(f'/id/products/{ID}',follow_redirects=False)
    assert html.status_code==303 and html.headers['location']==f'/#{ID}'
    assert client.get(f'/id/products/{uuid4()}').status_code==404

def test_seed_is_idempotent_and_preserves_edits(client):
    from fastapi.testclient import TestClient
    from apps.api.main import app
    data=payload();data['title']='Säilyvä muokkaus'
    assert client.put(f'/api/v1/products/{ID}',json=data).status_code==200
    assert client.delete(f"/api/v1/products/{FIXTURES[1]['id']}").status_code==204
    with TestClient(app) as restarted:
        assert restarted.get('/api/v1/products').json()['total']==2
        assert restarted.get(f'/api/v1/products/{ID}').json()['title']=='Säilyvä muokkaus'
        assert restarted.get(f"/api/v1/products/{FIXTURES[1]['id']}").status_code==404
