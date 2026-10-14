"""Real PostgreSQL upgrades from independently defined, pre-Alembic phase 1 DDL."""
from datetime import datetime, timezone
import json
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import MetaData, inspect, text

from apps.api.main import app, engine
from apps.api.migrate import upgrade_database


@pytest.fixture
def migration_database():
    assert engine.url.database == 'catalog_test', 'Refuse to reset a non-test database'
    def clear():
        with engine.begin() as connection:
            metadata = MetaData()
            metadata.reflect(connection)
            metadata.drop_all(connection)
    clear()
    yield engine
    clear()


def create_legacy(engine, *, marker=True):
    # Matches main's phase 1 schema, not the new ORM models or migration implementation.
    with engine.begin() as connection:
        connection.execute(text('''CREATE TABLE products (
            id UUID NOT NULL PRIMARY KEY, title VARCHAR(200) NOT NULL,
            description VARCHAR(5000) NOT NULL, provider VARCHAR(200) NOT NULL,
            theme VARCHAR(100) NOT NULL, metadata JSONB NOT NULL,
            modified_at TIMESTAMP WITH TIME ZONE NOT NULL)'''))
        for field in ('title','provider','theme'):
            connection.execute(text(f'CREATE INDEX ix_products_{field} ON products ({field})'))
        connection.execute(text('CREATE TABLE demo_initialization (name VARCHAR(100) NOT NULL PRIMARY KEY)'))
        if marker:
            connection.execute(text("INSERT INTO demo_initialization VALUES ('phase-1-fixtures')"))


def legacy_rows(engine):
    with engine.connect() as connection:
        return [dict(row) for row in connection.execute(text('''SELECT id,title,description,
            provider,theme,metadata,modified_at FROM products ORDER BY id''')).mappings()]


@pytest.mark.parametrize("marker", [True, False])
def test_legacy_upgrade_preserves_every_field_and_does_not_merge_names(migration_database, marker):
    create_legacy(engine, marker=marker)
    fixture = json.loads(Path('fixtures/products.json').read_text())[0]
    metadata = {k:v for k,v in fixture.items() if k not in ('id','title','description','provider','theme')}
    metadata['purpose'] = 'Käyttäjän muuttama käyttötarkoitus äöå'
    metadata['extraPreservedField'] = {'nested': [1, 'saa säilyä', False]}
    timestamp = datetime(2025, 6, 2, 10, 11, 12, 345678, tzinfo=timezone.utc)
    with engine.begin() as connection:
        for product_id in (fixture['id'], str(uuid4())):
            connection.execute(text('''INSERT INTO products VALUES
                (:id,:title,:description,:provider,:theme,CAST(:metadata AS JSONB),:modified)'''),
                dict(id=product_id, title='Muokattu tuote '+product_id,
                     description='Käyttäjän muokkaus; ei alkuperäinen fixture', provider='Samanniminen tarjoaja',
                     theme='Muokattu teema', metadata=json.dumps(metadata), modified=timestamp))
    before = legacy_rows(engine)
    upgrade_database(engine)
    assert legacy_rows(engine) == before
    with engine.connect() as connection:
        organizations = connection.execute(text('SELECT * FROM organizations')).mappings().all()
        assert len(organizations) == 2
        assert len({row['id'] for row in organizations}) == 2
        assert all(row['legal_name']=='Samanniminen tarjoaja' and row['country']=='ZZ'
                   and row['identifiers']==[] and row['synthetic'] for row in organizations)
        assert {row['legacy_product_id'] for row in organizations} == {row['id'] for row in before}
        references = connection.execute(text('SELECT provider_organization_id FROM products')).scalars().all()
        assert set(references)=={row['id'] for row in organizations}
    # Repeated upgrade and real app restarts must preserve data, IDs and references.
    upgrade_database(engine)
    with TestClient(app) as client:
        assert client.get('/api/v1/products').json()['total']==2
        product = client.get(f"/api/v1/products/{fixture['id']}").json()
        assert product['provider']=='Samanniminen tarjoaja'
        assert product['purpose']==metadata['purpose']
    assert legacy_rows(engine)==before


def test_empty_upgrade_and_repeat_start_seed_only_once(migration_database):
    upgrade_database(engine)
    with engine.connect() as connection:
        assert connection.scalar(text('SELECT version_num FROM alembic_version'))=='0003_auth'
        assert connection.scalar(text('SELECT count(*) FROM products'))==0
    with TestClient(app) as client:
        products = client.get('/api/v1/products').json()['items']
        assert len(products)==3
        original_ids = {p['id'] for p in products}
        original_orgs = {p['providerOrganizationId'] for p in products}
    for _ in range(2):
        upgrade_database(engine)
        with TestClient(app) as client:
            assert {p['id'] for p in client.get('/api/v1/products').json()['items']} == original_ids
            assert {o['id'] for o in client.get('/api/v1/organizations').json()['items']} == original_orgs
    inspector = inspect(engine)
    fk = inspector.get_foreign_keys('products')
    assert fk[0]['referred_table']=='organizations'
    assert fk[0]['options']['ondelete']=='RESTRICT'
    assert not next(c for c in inspector.get_columns('products') if c['name']=='provider_organization_id')['nullable']


def test_unmarked_empty_legacy_is_not_reseeded(migration_database):
    create_legacy(engine, marker=False)
    upgrade_database(engine)
    with TestClient(app) as client:
        assert client.get('/api/v1/products').json()['total']==0


def test_unknown_schema_aborts_without_partial_changes(migration_database):
    create_legacy(engine)
    with engine.begin() as connection:
        connection.execute(text('ALTER TABLE products ADD COLUMN unexpected TEXT'))
    with pytest.raises(RuntimeError, match='Poikkeavat sarakkeet'):
        upgrade_database(engine)
    assert 'organizations' not in inspect(engine).get_table_names()
    assert 'alembic_version' not in inspect(engine).get_table_names()
    assert 'unexpected' in {c['name'] for c in inspect(engine).get_columns('products')}


def test_initial_revision_matches_phase1_and_can_be_upgraded(migration_database):
    upgrade_database(engine, '0001_phase1')
    assert set(inspect(engine).get_table_names())=={'products','demo_initialization','alembic_version'}
    assert {c['name'] for c in inspect(engine).get_columns('products')}=={
        'id','title','description','provider','theme','metadata','modified_at'}
    upgrade_database(engine, '0001_phase1')
    upgrade_database(engine)
    with engine.connect() as connection:
        assert connection.scalar(text('SELECT version_num FROM alembic_version'))=='0003_auth'


def test_phase2a_upgrade_preserves_organizations_and_products(migration_database):
    from uuid import uuid4
    upgrade_database(engine,'0002_organizations')
    organization_id,product_id=uuid4(),uuid4()
    with engine.begin() as connection:
        connection.execute(text('''INSERT INTO organizations (id,legal_name,country,identifiers,synthetic)
            VALUES (:id,'Aiempi organisaatio','FI','[{"scheme":"demo","value":"säilyvä-tunniste"}]',true)'''),{'id':organization_id})
        connection.execute(text('''INSERT INTO products (id,title,description,provider,theme,metadata,modified_at,provider_organization_id)
            VALUES (:id,'Muokattu 2A-tuote','Säilytettävä kuvaus','Aiempi organisaatio','Testi',
            CAST(:metadata AS JSONB),'2026-01-02T03:04:05Z',:org)'''),{'id':product_id,'org':organization_id,'metadata':json.dumps({'synthetic':True,'extra':{'important':42}})})
        connection.execute(text("INSERT INTO demo_initialization VALUES ('phase-1-fixtures')"))
    before=legacy_rows(engine)
    with engine.connect() as connection:
        organization_before=dict(connection.execute(text('SELECT * FROM organizations')).mappings().one())
    upgrade_database(engine)
    upgrade_database(engine)
    with TestClient(app) as client:
        assert client.get('/api/v1/products').json()['total']==1
        assert client.get(f'/api/v1/products/{product_id}').json()['providerOrganizationId']==str(organization_id)
    assert legacy_rows(engine)==before
    with engine.connect() as connection:
        assert dict(connection.execute(text('SELECT * FROM organizations')).mappings().one())==organization_before
        # Custom organizations never receive demo rights solely because their names or fields look familiar.
        assert connection.scalar(text('SELECT count(*) FROM organization_memberships'))==0
