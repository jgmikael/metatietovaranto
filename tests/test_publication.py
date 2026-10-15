from concurrent.futures import ThreadPoolExecutor
from uuid import UUID,uuid4
from fastapi.testclient import TestClient
from sqlalchemy import select,text,func,event
from sqlalchemy.orm import Session
from sqlalchemy.exc import DBAPIError
import pytest

from apps.api.main import app,engine
from apps.api.models import Draft,ProductVersion,AuditEvent,OutboxEvent,OrganizationMembership,ProfileSnapshot
from conftest import authenticate
from helpers import body,create,change,import_profile,publish,ORG,ID


def ready_draft(client):return create(client,body()|{'profileSnapshotId':import_profile(client)['id']})

def submit(client,draft):
    response=client.post(f"/api/v1/drafts/{draft['draftId']}/submit",headers={'If-Match':draft['etag']})
    assert response.status_code==200,response.text
    return response.json()

def approve(client,draft):
    authenticate(client,'separate-reviewer',[UUID(ORG)],role='publisher')
    response=client.post(f"/api/v1/drafts/{draft['draftId']}/reviews",json={'decision':'approved','reason':'Lähdeilmoitus ja täydellinen SHACL-graafi tarkastettu','sourceReviewed':True},headers={'If-Match':draft['etag']})
    assert response.status_code==200,response.text
    return response.json()


def test_private_routes_do_not_leak_drafts_or_artifacts(client):
    draft=ready_draft(client);snapshot=draft['profileSnapshotId']
    with TestClient(app) as anonymous:
        for path in (f"/api/v1/products/{draft['id']}",f"/api/v1/products/{draft['id']}/export",f"/id/products/{draft['id']}",f'/api/v1/profile-snapshots/{snapshot}'):
            assert anonymous.get(path,follow_redirects=False).status_code==404
        assert anonymous.get('/api/v1/profile-snapshots').json()['items']==[]
        assert anonymous.get('/api/v1/catalog/export').json()['items']==[]
        assert anonymous.get(f"/api/v1/drafts/{draft['draftId']}").status_code==401
    with TestClient(app) as outsider:
        authenticate(outsider,'unassigned')
        assert outsider.get(f"/api/v1/drafts/{draft['draftId']}").status_code==404
        assert outsider.get(f"/api/v1/products/{draft['id']}/audit-events").status_code==404
        assert outsider.get(f'/api/v1/profile-snapshots/{snapshot}').status_code==404


def test_incomplete_profile_cannot_submit_and_cannot_forge_status(client):
    draft=create(client)
    assert client.post(f"/api/v1/drafts/{draft['draftId']}/submit",headers={'If-Match':draft['etag']}).status_code==422
    assert client.post('/api/v1/products',json=body()|{'status':'approved'}).status_code==422
    assert client.post('/api/v1/products',json=body()|{'reviewer':'forged'}).status_code==422


def test_self_approval_blocked_and_edits_invalidate_approval(client):
    draft=ready_draft(client)
    subject=client.get('/auth/me').json()['username']
    with Session(engine) as session:
        contributor=session.get(Draft,UUID(draft['draftId'])).contributors[-1]
        member=session.get(OrganizationMembership,(contributor,UUID(ORG)));member.role='publisher';session.commit()
    submitted=submit_as_publisher_test(client,draft,contributor)
    response=client.post(f"/api/v1/drafts/{draft['draftId']}/reviews",json={'decision':'approved','reason':'Oma hyväksyntäyritys','sourceReviewed':True},headers={'If-Match':submitted['etag']})
    assert response.status_code==403
    approved=approve(client,submitted)
    authenticate(client,'new-editor',[UUID(ORG)])
    updated=change(client,approved,body()|{'profileSnapshotId':draft['profileSnapshotId'],'title':'Hyväksynnän jälkeinen muutos'})
    assert updated['status']=='draft' and updated['contentHash']!=approved['contentHash']
    authenticate(client,'separate-reviewer',[UUID(ORG)],role='publisher')
    assert client.post(f"/api/v1/drafts/{draft['draftId']}/publish",json={'version':'1.0.0'},headers={'If-Match':updated['etag'],'Idempotency-Key':str(uuid4())}).status_code==409


def submit_as_publisher_test(client,draft,contributor):
    # Make the contributor an editor to submit, then a publisher to test the separation-of-duties rule itself.
    with Session(engine) as session:
        session.get(OrganizationMembership,(contributor,UUID(ORG))).role='editor';session.commit()
    submitted=submit(client,draft)
    with Session(engine) as session:
        session.get(OrganizationMembership,(contributor,UUID(ORG))).role='publisher';session.commit()
    return submitted


def test_published_snapshot_survives_new_draft_and_new_release(client):
    draft=ready_draft(client);first=publish(client,draft)
    private=client.get(f"/api/v1/products/{draft['id']}/draft").json()
    response=client.post(f"/api/v1/products/{draft['id']}/drafts",headers={'If-Match':private['etag']});assert response.status_code==200
    next_draft=change(client,response.json(),body()|{'profileSnapshotId':draft['profileSnapshotId'],'title':'Uusi versio'})
    assert client.get(f"/api/v1/products/{draft['id']}").json()==first
    assert client.get(f"/api/v1/products/{draft['id']}/versions/1.0.0").json()==first
    second=publish(client,next_draft,'1.1.0')
    assert second['title']=='Uusi versio'
    assert second['issuanceBinding']['productVersion']=='1.1.0'
    assert client.get(f"/api/v1/products/{draft['id']}/export?format=json&version=1.0.0").json()==first
    assert client.get(f"/id/products/{draft['id']}/versions/1.0.0",headers={'Accept':'application/json'}).json()==first
    assert client.get(f"/id/products/{draft['id']}/versions/1.0.0",headers={'Accept':'application/ld+json'}).json()['@id']==first['versionUri']
    assert client.get(f"/api/v1/products/{draft['id']}/versions/1.0.0").json()==first
    assert client.get(f"/api/v1/products/{draft['id']}").json()==second
    assert client.delete(f"/api/v1/products/{draft['id']}",headers={'If-Match':'"8"'}).status_code in (409,412)


def test_publish_idempotency_and_append_only_storage(client):
    draft=approve(client,submit(client,ready_draft(client)))
    url=f"/api/v1/drafts/{draft['draftId']}/publish";headers={'If-Match':draft['etag'],'Idempotency-Key':'same-publish'}
    result=client.post(url,json={'version':'1.0.0'},headers=headers);assert result.status_code==200
    assert client.post(url,json={'version':'1.0.0'},headers=headers).json()==result.json()
    assert client.post(url,json={'version':'2.0.0'},headers=headers).status_code==409
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(ProductVersion))==1
        assert session.scalar(select(func.count()).select_from(OutboxEvent))==1
        assert session.scalars(select(AuditEvent).where(AuditEvent.action=='product.published')).one().details['profileHash']
    for table,statement in [('product_versions','UPDATE product_versions SET checksum=checksum'),('profile_snapshots','DELETE FROM profile_snapshots'),('audit_events','DELETE FROM audit_events'),('reviews','DELETE FROM reviews')]:
        with pytest.raises(DBAPIError):
            with engine.begin() as connection:connection.execute(text(statement))


def test_publication_rollback_is_atomic(client):
    draft=approve(client,submit(client,ready_draft(client)))
    def fail_outbox(mapper,connection,target):raise RuntimeError('simulated transaction failure')
    event.listen(OutboxEvent,'before_insert',fail_outbox)
    try:
        with TestClient(app,raise_server_exceptions=False) as failing:
            failing.cookies.update(client.cookies);failing.headers.update(client.headers)
            response=failing.post(f"/api/v1/drafts/{draft['draftId']}/publish",json={'version':'1.0.0'},headers={'If-Match':draft['etag'],'Idempotency-Key':'atomic'})
            assert response.status_code==500
    finally:event.remove(OutboxEvent,'before_insert',fail_outbox)
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(ProductVersion))==0
        assert session.scalar(select(func.count()).select_from(OutboxEvent))==0
        assert session.get(Draft,UUID(draft['draftId'])).status=='approved'
    assert client.post(f"/api/v1/drafts/{draft['draftId']}/publish",json={'version':'1.0.0'},headers={'If-Match':draft['etag'],'Idempotency-Key':'atomic'}).status_code==200


def test_real_concurrent_updates_only_one_wins(client):
    draft=create(client)
    cookies=dict(client.cookies);headers=dict(client.headers)
    def update(title):
        with TestClient(app) as actor:
            actor.cookies.update(cookies);actor.headers.update(headers)
            return actor.put('/api/v1/products/'+draft['id'],json=body()|{'title':title},headers={'If-Match':draft['etag']}).status_code
    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes=list(executor.map(update,['A','B']))
    assert sorted(outcomes)==[200,412]


def test_usable_vc_delivery_requires_metadata_and_pins_binding(client):
    profile=import_profile(client)
    data=body()|{'profileSnapshotId':profile['id'],'issuance':{'serviceAvailability':'sandbox'}}
    draft=create(client,data)
    errors=client.post(f"/api/v1/drafts/{draft['draftId']}/validate",headers={'If-Match':draft['etag']})
    assert errors.status_code==200
    assert client.post(f"/api/v1/drafts/{draft['draftId']}/submit",headers={'If-Match':draft['etag']}).status_code==422
    paths={element['semanticUri']:'credentialSubject.companyName' for element in profile['elements'] if element['semanticUri']}
    data['issuance']|={'issuerOrganizationId':ORG,'operatorOrganizationId':ORG,'sourceProviderOrganizationId':ORG,
        'issuanceInitiationUrl':'https://issuer.fi/request?product=synthetic-demo',
        'credentialIssuer':'https://issuer.fi/','credentialConfigurationIds':['demo-config'],
        'credentialProfile':{'vcTypes':['VerifiableCredential','urn:synthetic:DemoCredential'],
            'contexts':['https://www.w3.org/ns/credentials/v2'],'fieldMappings':paths,'securityMechanism':'Data Integrity (declared demo metadata)'},
        'walletCompatibility':[{'profile':'Synthetic demo wallet','version':'1','status':'declared'}],
        'subjectTypes':['legalPerson'],'representationRequirements':'Myöntäjä tarkistaa edustamisoikeuden',
        'validityPolicy':'Myöntäjä päättää voimassaolon','statusPolicy':'Myöntäjä kertoo statuksen','support':'Synteettinen tukikuvaus'}
    updated=change(client,draft,data)
    result=publish(client,updated)
    assert result['issuance']['issuanceInitiationUrl']=='https://issuer.fi/request?product=synthetic-demo'
    assert result['issuanceBinding']['profileSnapshotSha256']==profile['sha256']
    assert result['issuance']['walletCompatibility'][0]['status']=='declared'
