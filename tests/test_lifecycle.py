"""Version lifecycle commands, SQL transactions, immutable exports and public visibility."""
from concurrent.futures import ThreadPoolExecutor
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, func, text, event
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session
from rdflib import Graph, URIRef, Literal

from apps.api.main import app, engine
from apps.api.models import LifecycleEvent, LifecycleOutboxEvent, AuditEvent, ProductVersion, Organization
from apps.api.profiles import checksum
from conftest import authenticate
from helpers import ORG, body, create, change, import_profile, publish


def ready(client):
    profile=import_profile(client)
    return publish(client,create(client,body()|{'profileSnapshotId':profile['id']}))


def state_url(item):return f"/api/v1/products/{item['id']}/versions/{item['version']}/lifecycle"


def state(client,item):
    response=client.get(state_url(item));assert response.status_code==200,response.text
    assert response.headers['etag']==response.json()['etag']
    return response.json()


def publisher(client,org=ORG):authenticate(client,'lifecycle-publisher-'+org,[UUID(org)],role='publisher')


def command(client,item,status='deprecated',*,current=None,key=None,**fields):
    current=current or state(client,item)
    return client.post('/api/v1/products/'+item['id']+'/lifecycle-events',
        json={'version':item['version'],'status':status,'reason':'Synteettisen testin julkinen elinkaariperustelu',**fields},
        headers={'If-Match':current['etag'],'Idempotency-Key':key or str(uuid4())})


def second_version(client,first):
    authenticate(client,'next-version-editor',[UUID(ORG)])
    draft=client.get('/api/v1/products/'+first['id']+'/draft').json()
    draft=client.post('/api/v1/products/'+first['id']+'/drafts',headers={'If-Match':draft['etag']}).json()
    draft=change(client,draft,body()|{'title':'Uudempi synteettinen sisältö','profileSnapshotId':first['profileSnapshotId']})
    return publish(client,draft,'2.0.0')


def test_initial_state_and_immutable_representation_are_backward_compatible(client):
    item=ready(client);initial=state(client,item)
    assert initial['status']=='published' and initial['revision']==0 and initial['events']==[]
    assert initial['versionContentHash']==item['contentHash']
    assert client.get('/api/v1/products/'+item['id']).json()==item
    for path in [f"/api/v1/products/{item['id']}/versions/1.0.0",f"/id/products/{item['id']}/versions/1.0.0",f"/api/v1/products/{item['id']}/export?version=1.0.0"]:
        response=client.get(path,headers={'Accept':'application/json'})
        assert response.json()==item and response.headers['etag']=='"'+item['contentHash']+'"'
        assert response.headers['X-Product-Lifecycle-Status']=='published'
        assert initial['uri'] in response.headers['link'] and 'describedby' in response.headers['link']
    assert client.get(state_url(item).replace('1.0.0','9.0.0')).status_code==404


def test_deprecation_with_replacement_keeps_old_snapshot_and_separate_live_exports(client):
    first=ready(client);second=second_version(client,first);publisher(client)
    old_raw=client.get(f"/api/v1/products/{first['id']}/versions/1.0.0").json()
    response=command(client,first,replacementVersion='2.0.0')
    assert response.status_code==201,response.text
    life=response.json();assert life['status']=='deprecated' and life['replacementVersion']=='2.0.0'
    assert life['replacementVersionUri']==second['versionUri'] and life['revision']==1
    assert state(client,first)==life
    assert 'actor' not in str(life) and 'lifecycle-publisher' not in str(life)
    response=client.get(f"/api/v1/products/{first['id']}/versions/1.0.0")
    assert response.json()==old_raw and response.headers['X-Product-Lifecycle-Status']=='deprecated'
    assert client.get('/api/v1/products/'+first['id']).json()==second
    versions=client.get('/api/v1/products/'+first['id']+'/versions').json()['items']
    assert [item['lifecycle']['status'] for item in versions]==['published','deprecated']
    # Live view and export include status only for versions with events.
    assert command(client,second).status_code==201
    live=client.get('/api/v1/products/'+first['id']).json()
    assert live['lifecycle']['status']=='deprecated'
    assert client.get('/api/v1/products/'+first['id']+'/export').json()==live
    graph=Graph().parse(data=client.get('/api/v1/products/'+first['id']+'/export?format=jsonld').text,format='json-ld')
    assert (URIRef(live['lifecycle']['uri']),URIRef('https://example.org/metatietovaranto/demo/status'),Literal('deprecated')) in graph
    assert client.get('/api/v1/products?lifecycleStatus=deprecated').json()['total']==1
    assert client.get('/api/v1/products?lifecycleStatus=published').json()['total']==0


def test_withdraw_latest_never_falls_back_and_all_search_exports_keep_explicit_history(client):
    first=ready(client);second=second_version(client,first);publisher(client)
    assert command(client,second,'withdrawn').status_code==201
    current=client.get('/api/v1/products/'+first['id']).json()
    assert current['version']=='2.0.0' and current['lifecycle']['status']=='withdrawn'
    assert client.get('/api/v1/products').json()['total']==0
    for status in ('all','withdrawn'):
        result=client.get('/api/v1/products',params={'lifecycleStatus':status,'limit':1}).json()
        assert result['total']==1 and result['items'][0]['lifecycle']['status']=='withdrawn'
        assert client.get('/api/v1/products',params={'lifecycleStatus':status,'offset':1}).json()['items']==[]
    assert client.get('/api/v1/products?lifecycleStatus=bad').status_code==422
    assert client.get('/api/v1/catalog/export').json()['items']==[]
    exported=client.get('/api/v1/catalog/export?includeWithdrawn=true').json()['items']
    assert exported==[current]
    assert client.get('/api/v1/catalog/export?format=jsonld').json()['dcat:dataset']==[]
    assert client.get('/api/v1/catalog/export?format=jsonld&includeWithdrawn=true').json()['dcat:dataset'][0]['demo:lifecycle']['demo:status']=='withdrawn'
    assert client.get('/id/products/'+first['id'],headers={'Accept':'application/json'}).json()==current
    assert client.get('/id/products/'+first['id'],follow_redirects=False).status_code==303
    for version in ('1.0.0','2.0.0'):
        response=client.get(f"/api/v1/products/{first['id']}/export?format=json&version={version}")
        assert 'lifecycle' not in response.json()
    assert client.get(f"/api/v1/products/{first['id']}/versions/1.0.0").json()==first


@pytest.mark.parametrize('role',['editor','reader','reviewer','foreignPublisher','anonymous'])
def test_only_owner_publisher_can_change_lifecycle(client,role):
    item=ready(client)
    if role=='anonymous':client.cookies.clear()
    elif role=='foreignPublisher':authenticate(client,'foreign-publisher',[],role='publisher')
    else:authenticate(client,'only-'+role,[UUID(ORG)],role=role)
    response=command(client,item)
    assert response.status_code==(401 if role=='anonymous' else 404),response.text
    assert state(client,item)['revision']==0


def test_csrf_if_match_idempotency_and_terminal_transitions(client):
    item=ready(client);publisher(client);initial=state(client,item)
    url='/api/v1/products/'+item['id']+'/lifecycle-events'
    data={'version':'1.0.0','status':'deprecated','reason':'Julkinen synteettinen testiperustelu'}
    assert client.post(url,json=data).status_code==428
    assert client.post(url,json=data,headers={'Idempotency-Key':'missing-match'}).status_code==428
    for etag in ('"0"','"'+item['contentHash']+'"','*'):
        assert command(client,item,current={'etag':etag}).status_code==412
    csrf=client.headers.pop('X-CSRF-Token')
    assert command(client,item).status_code==403
    client.headers['X-CSRF-Token']=csrf
    assert command(client,item,reason='   ').status_code==422
    for status in ('published','archived','retired'):
        assert command(client,item,status).status_code==422
    first=command(client,item,current=initial,key='retry')
    assert first.status_code==201
    assert command(client,item,current=initial,key='retry').json()==first.json()
    assert command(client,item,current=initial,key='retry',reason='Toinen sisältö samalla avaimella').status_code==409
    assert command(client,item,current=initial).status_code==412
    assert command(client,item).status_code==409
    withdrawn=command(client,item,'withdrawn');assert withdrawn.status_code==201
    assert command(client,item,current=initial,key='retry').json()==first.json()
    assert state(client,item)==withdrawn.json()
    assert command(client,item,'deprecated').status_code==409
    assert command(client,item,'withdrawn').status_code==409


def test_invalid_replacements_cannot_create_cycles_or_cross_product_links(client):
    first=ready(client);second=second_version(client,first);other=ready(client);publisher(client)
    assert command(client,first,replacementVersion='1.0.0').status_code==409
    assert command(client,second,replacementVersion='1.0.0').status_code==409
    assert command(client,first,replacementVersion='9.0.0').status_code==404
    assert command(client,other,replacementVersion='2.0.0').status_code==404
    assert command(client,first,'withdrawn',replacementVersion='2.0.0').status_code==409
    assert command(client,second,'withdrawn').status_code==201
    assert command(client,first,replacementVersion='2.0.0').status_code==409
    assert state(client,first)['revision']==0


@pytest.mark.parametrize('same_key',[False,True])
def test_concurrent_commands_preserve_single_transition(client,same_key):
    item=ready(client);publisher(client);initial=state(client,item)
    cookies=dict(client.cookies);headers=dict(client.headers)
    def write(index):
        with TestClient(app) as actor:
            actor.cookies.update(cookies);actor.headers.update(headers)
            return command(actor,item,current=initial,key='same' if same_key else str(index)).status_code
    with ThreadPoolExecutor(max_workers=2) as executor:results=list(executor.map(write,[1,2]))
    assert sorted(results)==([201,201] if same_key else [201,412])
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(LifecycleEvent))==1
        assert session.scalar(select(func.count()).select_from(LifecycleOutboxEvent))==1
        assert session.scalar(select(func.count()).select_from(AuditEvent).where(AuditEvent.action=='version.deprecated'))==1


def test_rollback_and_append_only_trigger_keep_original_publication_and_retry_safe(client):
    item=ready(client);publisher(client);initial=state(client,item)
    def fail_outbox(mapper,connection,target):raise RuntimeError('simulated lifecycle transaction failure')
    event.listen(LifecycleOutboxEvent,'before_insert',fail_outbox)
    try:
        with TestClient(app,raise_server_exceptions=False) as failing:
            failing.cookies.update(client.cookies);failing.headers.update(client.headers)
            assert command(failing,item,current=initial,key='atomic').status_code==500
    finally:event.remove(LifecycleOutboxEvent,'before_insert',fail_outbox)
    assert state(client,item)==initial
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(LifecycleEvent))==0
        assert session.scalar(select(func.count()).select_from(LifecycleOutboxEvent))==0
        assert session.scalar(select(func.count()).select_from(AuditEvent).where(AuditEvent.action=='version.deprecated'))==0
    assert command(client,item,current=initial,key='atomic').status_code==201
    for table in ('lifecycle_events','lifecycle_outbox_events','product_versions'):
        for statement in (f'DELETE FROM {table}',f'UPDATE {table} SET id=id'):
            with pytest.raises(DBAPIError):
                with engine.begin() as connection:connection.execute(text(statement))
    with Session(engine) as session:
        row=session.scalar(select(ProductVersion).where(ProductVersion.product_id==UUID(item['id'])))
        assert checksum(row.content)==row.checksum==item['contentHash']
    assert client.get(f"/api/v1/products/{item['id']}/versions/1.0.0").json()==item
    assert client.get(f"/api/v1/products/{item['id']}/audit-events").json()['items'][-1]['actorId'].startswith('lifecycle-publisher')


def test_lifecycle_restart_preserves_draft_and_new_publication_does_not_reset_history(client):
    first=ready(client);publisher(client)
    assert command(client,first,'withdrawn').status_code==201
    before=state(client,first)
    draft=client.get('/api/v1/products/'+first['id']+'/draft').json()
    with TestClient(app):pass
    assert state(client,first)==before and client.get('/api/v1/products/'+first['id']+'/draft').json()==draft
    second=second_version(client,first)
    assert state(client,first)==before and state(client,second)['status']=='published'
    assert client.get('/api/v1/products').json()['total']==1
    assert client.get('/api/v1/products/'+first['id']).json()==second


def test_changing_provider_does_not_grant_lifecycle_rights_to_provider_publisher(client):
    profile=import_profile(client);draft=create(client,body()|{'profileSnapshotId':profile['id']})
    with Session(engine) as session:other=session.scalar(select(Organization.id).where(Organization.id!=UUID(ORG)))
    data=body()|{'profileSnapshotId':profile['id'],'providerOrganizationId':str(other)}
    draft=change(client,draft,data);item=publish(client,draft)
    publisher(client,str(other));assert command(client,item).status_code==404
    publisher(client);assert command(client,item).status_code==201


def test_earliest_2c_snapshot_missing_version_uri_remains_readable_and_unchanged(client):
    first=ready(client)
    # Independently represent the early 2C layout in test storage: these keys did not yet exist.
    with Session(engine) as session:
        earlier=session.scalar(select(ProductVersion).where(ProductVersion.product_id==UUID(first['id'])))
        content=dict(earlier.content);content.pop('versionUri');content.pop('version')
        content['preservedUnknown']={'important':['äöå',False,17]}
        session.add(ProductVersion(product_id=earlier.product_id,version='2.0.0',sequence=2,content=content,
            checksum=checksum(content),profile_snapshot_id=earlier.profile_snapshot_id,review_id=earlier.review_id,
            publisher=earlier.publisher,created_at=earlier.created_at))
        session.commit()
    expected=content|{'version':'2.0.0','contentHash':checksum(content)}
    path=f"/api/v1/products/{first['id']}/versions/2.0.0"
    assert client.get(path).json()==expected
    jsonld=client.get(f"/api/v1/products/{first['id']}/export?format=jsonld&version=2.0.0").json()
    assert client.get('/api/v1/products').json()['total']==1
    life=state(client,expected)
    assert life['status']=='published' and life['versionUri']==content['uri']+'/versions/2.0.0'
    publisher(client)
    assert command(client,expected,'withdrawn').status_code==201
    assert client.get('/api/v1/products?lifecycleStatus=withdrawn').json()['total']==1
    assert client.get(path).json()==expected
    assert client.get(f"/api/v1/products/{first['id']}/export?format=jsonld&version=2.0.0").json()==jsonld
    with Session(engine) as session:
        row=session.scalar(select(ProductVersion).where(ProductVersion.product_id==UUID(first['id']),ProductVersion.sequence==2))
        assert row.content==content and row.checksum==checksum(content)
