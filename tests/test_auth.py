"""Authorization denial cases exercise the same database/session path as live OIDC."""
from datetime import timedelta
from uuid import UUID
from urllib.parse import urlsplit, parse_qs
import json
from pathlib import Path
import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session
from conftest import authenticate
from apps.api.main import engine
from apps.api.models import Product, OrganizationMembership, WebSession, OAuthFlow
from apps.api.auth import digest, now, SESSION_COOKIE


def payload(client, index=0):
    product=client.get('/api/v1/products').json()['items'][index]
    fields=json.loads(Path('fixtures/products.json').read_text())[0].keys()
    return product, {key:product[key] for key in fields if key not in ('id','provider')} | {
        'providerOrganizationId':product['providerOrganizationId']}


def test_anonymous_reads_but_cannot_write(anonymous_client):
    client=anonymous_client
    product,data=payload(client)
    assert client.get('/auth/me').json()['authenticated'] is False
    assert client.get('/api/v1/catalog/export?format=jsonld').status_code==200
    assert client.post('/api/v1/products',json=data).status_code==401
    assert client.put(f"/api/v1/products/{product['id']}",json=data).status_code==401
    assert client.delete(f"/api/v1/products/{product['id']}").status_code==401
    client.cookies.set(SESSION_COOKIE,'forged-session')
    assert client.post('/api/v1/products',json=data).status_code==401


def test_cross_organization_read_only_and_forged_identity_denied(anonymous_client):
    client=anonymous_client
    own,data=payload(client,0)
    other,other_data=payload(client,1)
    authenticate(client,'editor-a',[UUID(own['providerOrganizationId'])])
    assert client.put(f"/api/v1/products/{own['id']}",json=data).status_code==200
    for method,path,body in [('POST','/api/v1/products',other_data),
        ('PUT',f"/api/v1/products/{other['id']}",data),
        ('PUT',f"/api/v1/products/{own['id']}",other_data),
        ('DELETE',f"/api/v1/products/{other['id']}",None)]:
        response=client.request(method,path,json=body,headers={'X-Organization-ID':other['providerOrganizationId'],
                                                              'X-User-ID':'admin'})
        assert response.status_code==403
    # No denied request changes product ownership or contents.
    assert client.get(f"/api/v1/products/{other['id']}").json()==other
    assert client.get(f"/api/v1/products/{own['id']}").json()['providerOrganizationId']==own['providerOrganizationId']
    authenticate(client,'reader-a',[UUID(own['providerOrganizationId'])],role='reader')
    assert client.post('/api/v1/products',json=data).status_code==403
    assert client.put(f"/api/v1/products/{own['id']}",json=data).status_code==403
    assert client.delete(f"/api/v1/products/{own['id']}").status_code==403


def test_csrf_expiry_logout_and_revoked_membership(anonymous_client):
    client=anonymous_client
    product,data=payload(client)
    token=authenticate(client,'editor-a',[UUID(product['providerOrganizationId'])])
    assert client.post('/api/v1/products',json=data,headers={'X-CSRF-Token':''}).status_code==403
    assert client.post('/api/v1/products',json=data,headers={'X-CSRF-Token':'forged'}).status_code==403
    with Session(engine) as session:
        membership=session.get(OrganizationMembership,('editor-a',UUID(product['providerOrganizationId'])))
        session.delete(membership);session.commit()
    assert client.post('/api/v1/products',json=data).status_code==403
    response=client.post('/auth/logout')
    assert response.status_code==204
    client.cookies.set(SESSION_COOKIE,token)
    assert client.post('/api/v1/products',json=data).status_code==401
    token=authenticate(client,'editor-a',[UUID(product['providerOrganizationId'])])
    with Session(engine) as session:
        identity=session.get(WebSession,digest(token));identity.expires_at=now()-timedelta(seconds=1);session.commit()
    assert client.post('/api/v1/products',json=data).status_code==401


def test_login_pkce_cookie_state_and_replay_protection(anonymous_client):
    client=anonymous_client
    response=client.get('/auth/login',follow_redirects=False)
    assert response.status_code==303
    query=parse_qs(urlsplit(response.headers['location']).query)
    assert query['code_challenge_method']==['S256']
    assert query['scope']==['openid profile']
    cookie=response.headers['set-cookie'].lower()
    assert 'httponly' in cookie and 'samesite=lax' in cookie
    state=query['state'][0]
    assert client.get('/auth/callback?code=fake&state=wrong').status_code==400
    # State without the browser's flow cookie is rejected before any token exchange.
    client.cookies.clear()
    assert client.get('/auth/callback',params={'code':'fake','state':state}).status_code==400
    with Session(engine) as session:
        flow=session.get(OAuthFlow,digest(state));flow.expires_at=now()-timedelta(seconds=1);session.commit()
    assert client.get('/auth/callback',params={'code':'fake','state':state}).status_code==400
    assert response.headers['cache-control']=='no-store'


def test_memberships_are_not_restored_on_restart(anonymous_client):
    from fastapi.testclient import TestClient
    from apps.api.main import app
    with Session(engine) as session:
        count=len(session.scalars(select(OrganizationMembership)).all())
        assert count==3
        for member in session.scalars(select(OrganizationMembership)).all():
            session.delete(member)
        session.commit()
    with TestClient(app):
        with Session(engine) as session:
            assert session.scalars(select(OrganizationMembership)).all()==[]


def test_signed_id_token_validation():
    import jwt
    from cryptography.hazmat.primitives.asymmetric import rsa
    from apps.api.auth import verify_id_token, CLIENT_ID
    key=rsa.generate_private_key(public_exponent=65537,key_size=2048)
    public=json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(key.public_key()));public['kid']='test-key'
    claims={'sub':'test','iss':'https://issuer.example/realm','aud':CLIENT_ID,'exp':now()+timedelta(minutes=5),
            'iat':now(),'nonce':'expected-nonce'}
    def token(data):return jwt.encode(data,key,algorithm='RS256',headers={'kid':'test-key'})
    assert verify_id_token(token(claims),{'keys':[public]},issuer=claims['iss'],nonce='expected-nonce')['sub']=='test'
    for change in ({'iss':'https://wrong.example'},{'aud':'other-client'},{'nonce':'wrong'},
                   {'exp':now()-timedelta(seconds=1)},{'azp':'other-client'}):
        with pytest.raises(jwt.PyJWTError):
            verify_id_token(token(claims|change),{'keys':[public]},issuer=claims['iss'],nonce='expected-nonce')
    with pytest.raises(jwt.PyJWTError):
        verify_id_token(jwt.encode(claims,'f'*32,algorithm='HS256'),{'keys':[public]},issuer=claims['iss'],nonce='expected-nonce')


def test_callback_rejects_invalid_token_and_consumes_state(anonymous_client, monkeypatch):
    import httpx
    import apps.api.auth as auth
    client=anonymous_client
    response=client.get('/auth/login',follow_redirects=False)
    state=parse_qs(urlsplit(response.headers['location']).query)['state'][0]
    class Provider:
        def __init__(self, **kwargs):pass
        async def __aenter__(self):return self
        async def __aexit__(self,*args):pass
        async def post(self,*args,**kwargs):
            assert kwargs['data']['code_verifier']
            return httpx.Response(200,json={'id_token':'invalid'},request=httpx.Request('POST','http://provider'))
        async def get(self,*args,**kwargs):
            return httpx.Response(200,json={'keys':[]},request=httpx.Request('GET','http://provider'))
    monkeypatch.setattr(auth.httpx,'AsyncClient',Provider)
    response=client.get('/auth/callback',params={'code':'fake','state':state},follow_redirects=False)
    assert response.status_code==401
    assert SESSION_COOKIE not in response.cookies
    assert client.get('/auth/callback',params={'code':'fake','state':state}).status_code==400


def test_https_flow_cookie_and_proxy_boundary(anonymous_client):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from apps.api.auth import build_router
    secure_app=FastAPI()
    secure_app.include_router(build_router(engine,'https://private-codespace.example'))
    with TestClient(secure_app,base_url='https://private-codespace.example') as client:
        response=client.get('/auth/login',follow_redirects=False)
        assert 'secure' in response.headers['set-cookie'].lower()
        assert response.headers['location'].startswith('https://private-codespace.example/identity/')
    assert anonymous_client.get('/identity/admin/').status_code==404
    assert anonymous_client.get('/identity/realms/master/').status_code==404
    assert anonymous_client.get('/identity/resources/%2e%2e/admin/').status_code==404
