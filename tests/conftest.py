"""Integration tests require a separate PostgreSQL database; never truncate demo data."""
import os

os.environ['DATABASE_URL'] = os.getenv('TEST_DATABASE_URL', 'postgresql+psycopg://demo:demo@localhost:5432/catalog_test')
os.environ['DEMO_MODE'] = 'true'

import pytest
from fastapi.testclient import TestClient
from apps.api.main import app, engine, Product, DemoInitialization
from sqlalchemy import delete

@pytest.fixture
def client():
    if engine.url.database != 'catalog_test':
        raise RuntimeError('Testit vaativat erillisen catalog_test-tietokannan')
    with TestClient(app) as client:
        yield client
    with engine.begin() as connection:
        connection.execute(delete(Product))
        connection.execute(delete(DemoInitialization))
