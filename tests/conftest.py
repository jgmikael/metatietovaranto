"""Integration tests use only the separate, disposable PostgreSQL catalog_test DB."""
import os
os.environ['DATABASE_URL'] = os.getenv('TEST_DATABASE_URL', 'postgresql+psycopg://demo:demo@localhost:5432/catalog_test')
os.environ['DEMO_MODE'] = 'true'

from datetime import timedelta
import secrets
from uuid import uuid4
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select
from sqlalchemy.orm import Session
from apps.api.main import app, engine
from apps.api.models import Product, DemoInitialization, Organization, OrganizationMembership, WebSession, OAuthFlow
from apps.api.auth import digest, now, SESSION_COOKIE


@pytest.fixture
def anonymous_client():
    if engine.url.database != 'catalog_test':
        raise RuntimeError('Testit vaativat erillisen catalog_test-tietokannan')
    with TestClient(app) as client:
        yield client
    with engine.begin() as connection:
        for model in (OAuthFlow, WebSession, OrganizationMembership, Product, DemoInitialization, Organization):
            connection.execute(delete(model))


def authenticate(client, subject, organization_ids=(), role='editor'):
    """Install an opaque session in the test DB; no application auth bypass exists."""
    token, csrf = secrets.token_urlsafe(32), secrets.token_hex(32)
    with Session(engine) as session:
        for organization_id in organization_ids:
            if session.get(OrganizationMembership, (subject, organization_id)) is None:
                session.add(OrganizationMembership(subject=subject, organization_id=organization_id, role=role))
        session.add(WebSession(token_hash=digest(token), subject=subject, username='test-user',
                              csrf_token=csrf, expires_at=now()+timedelta(hours=1)))
        session.commit()
    client.cookies.set(SESSION_COOKIE, token)
    client.headers['X-CSRF-Token']=csrf
    return token


@pytest.fixture
def client(anonymous_client):
    # Existing CRUD tests run as an editor with explicit memberships to their test fixtures.
    with Session(engine) as session:
        ids=session.scalars(select(Organization.id)).all()
    authenticate(anonymous_client, 'test-'+str(uuid4()), ids)
    yield anonymous_client
