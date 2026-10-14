import json
from pathlib import Path
from uuid import uuid4, uuid5, NAMESPACE_URL

from rdflib import Graph, URIRef, Literal
from rdflib.namespace import DCTERMS, RDF, DCAT
from sqlalchemy import select
from sqlalchemy.orm import Session
from apps.api.main import engine, Product

FIXTURES = json.loads(Path('fixtures/products.json').read_text())
ID = FIXTURES[0]['id']

def payload():
    data = json.loads(json.dumps({k:v for k,v in FIXTURES[0].items() if k not in ('id','provider')}))
    data['providerOrganizationId'] = str(uuid5(NAMESPACE_URL, f'https://example.org/metatietovaranto/legacy-provider/{ID}'))
    return data

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
    for field in ('title','description','theme','source','purpose','limitations','accessConditions'):
        data=payload();data[field]='  '
        assert client.post('/api/v1/products',json=data).status_code==422
    for field,value in [('providerOrganizationId',str(uuid4())),('providerOrganizationId',''),('synthetic',False),('dataElements',[]),('availability','production'),('title','x'*201)]:
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


def test_organization_api_and_provider_selection(client):
    organizations=client.get('/api/v1/organizations').json()['items']
    assert len(organizations)==3
    for organization in organizations:
        assert organization['country']=='FI'
        assert organization['synthetic'] is True
        assert organization['identifiers'][0]['scheme']=='demo'
        assert client.get(f"/api/v1/organizations/{organization['id']}").json()==organization
    assert client.get(f'/api/v1/organizations/{uuid4()}').status_code==404
    assert client.get('/api/v1/organizations/not-a-uuid').status_code==422
    data=payload();data['providerOrganizationId']=organizations[0]['id']
    created=client.post('/api/v1/products',json=data).json()
    assert created['provider']==organizations[0]['legalName']
    assert created['providerOrganizationId']==organizations[0]['id']
    data['providerOrganizationId']=organizations[1]['id']
    updated=client.put(f"/api/v1/products/{created['id']}",json=data).json()
    assert updated['provider']==organizations[1]['legalName']
    assert client.get(f"/api/v1/products/{created['id']}/export?format=json").json()['provider']==organizations[1]['legalName']
    graph=Graph().parse(data=client.get(f"/api/v1/products/{created['id']}/export?format=jsonld").text,format='json-ld')
    publisher=graph.value(URIRef(updated['uri']),DCTERMS.publisher)
    assert str(publisher).endswith(organizations[1]['id'])
    assert graph.value(publisher,DCTERMS.title)==Literal(organizations[1]['legalName'])


def test_database_rejects_missing_or_unknown_provider_fk(client):
    from sqlalchemy import text
    from sqlalchemy.exc import IntegrityError
    import pytest
    for value in (None,uuid4()):
        with pytest.raises(IntegrityError):
            with engine.begin() as connection:
                connection.execute(text('UPDATE products SET provider_organization_id=:value WHERE id=:id'),
                                   {'value':value,'id':ID})
