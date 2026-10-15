"""Drafts, immutable profile/publication snapshots, reviews, audit and outbox."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg
from uuid import uuid4
import hashlib
import json

revision = "0004_publication"
down_revision = "0003_auth"
branch_labels = depends_on = None


def upgrade():
    op.add_column('products', sa.Column('owner_organization_id', pg.UUID(as_uuid=True), nullable=True))
    op.execute('UPDATE products SET owner_organization_id = provider_organization_id')
    op.alter_column('products', 'owner_organization_id', nullable=False)
    op.create_foreign_key('fk_products_owner', 'products', 'organizations', ['owner_organization_id'], ['id'])
    op.create_table('semantic_profiles',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True),
        sa.Column('profile_uri', sa.String(2048), unique=True))
    op.create_table('profile_snapshots',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True),
        sa.Column('profile_id', pg.UUID(as_uuid=True), sa.ForeignKey('semantic_profiles.id'), nullable=False),
        sa.Column('owner_organization_id', pg.UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('manifest', pg.JSONB(), nullable=False),
        sa.Column('checksum', sa.String(64), nullable=False),
        sa.Column('graph_hash', sa.String(128)),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False))
    op.create_table('drafts',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True),
        sa.Column('product_id', pg.UUID(as_uuid=True), sa.ForeignKey('products.id'), nullable=False, unique=True),
        sa.Column('content', pg.JSONB(), nullable=False),
        sa.Column('profile_snapshot_id', pg.UUID(as_uuid=True), sa.ForeignKey('profile_snapshots.id')),
        sa.Column('revision', sa.Integer(), nullable=False), sa.Column('status', sa.String(30), nullable=False),
        sa.Column('checksum', sa.String(64), nullable=False), sa.Column('contributors', pg.JSONB(), nullable=False),
        sa.Column('approved_review_id', pg.UUID(as_uuid=True)),
        sa.Column('modified_at', sa.DateTime(timezone=True), nullable=False))
    op.create_table('reviews',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True),
        sa.Column('draft_id', pg.UUID(as_uuid=True), sa.ForeignKey('drafts.id'), nullable=False),
        sa.Column('revision', sa.Integer(), nullable=False), sa.Column('checksum', sa.String(64), nullable=False),
        sa.Column('reviewer', sa.String(255), nullable=False), sa.Column('decision', sa.String(30), nullable=False),
        sa.Column('reason', sa.String(2000), nullable=False), sa.Column('source_reviewed', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False))
    op.create_table('product_versions',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True),
        sa.Column('product_id', pg.UUID(as_uuid=True), sa.ForeignKey('products.id'), nullable=False),
        sa.Column('version', sa.String(50), nullable=False), sa.Column('sequence', sa.Integer(), nullable=False),
        sa.Column('content', pg.JSONB(), nullable=False), sa.Column('checksum', sa.String(64), nullable=False),
        sa.Column('profile_snapshot_id', pg.UUID(as_uuid=True), sa.ForeignKey('profile_snapshots.id'), nullable=False),
        sa.Column('review_id', pg.UUID(as_uuid=True), sa.ForeignKey('reviews.id'), nullable=False),
        sa.Column('publisher', sa.String(255), nullable=False), sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint('product_id', 'version'), sa.UniqueConstraint('product_id', 'sequence'))
    op.create_table('audit_events',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', pg.UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('product_id', pg.UUID(as_uuid=True), nullable=False), sa.Column('actor', sa.String(255), nullable=False),
        sa.Column('action', sa.String(50), nullable=False), sa.Column('before_hash', sa.String(64)),
        sa.Column('after_hash', sa.String(64)), sa.Column('reason', sa.String(2000), nullable=False),
        sa.Column('details', pg.JSONB(), nullable=False), sa.Column('created_at', sa.DateTime(timezone=True), nullable=False))
    op.create_table('idempotent_operations',
        sa.Column('subject', sa.String(255), primary_key=True), sa.Column('operation', sa.String(100), primary_key=True),
        sa.Column('key', sa.String(128), primary_key=True), sa.Column('request_hash', sa.String(64), nullable=False),
        sa.Column('response', pg.JSONB(), nullable=False), sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False))
    op.create_table('outbox_events',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True),
        sa.Column('version_id', pg.UUID(as_uuid=True), sa.ForeignKey('product_versions.id'), nullable=False, unique=True),
        sa.Column('payload', pg.JSONB(), nullable=False), sa.Column('created_at', sa.DateTime(timezone=True), nullable=False))
    # Preserve all prior columns, IDs and timestamps. Legacy descriptions become private, incomplete drafts.
    bind = op.get_bind()
    for row in bind.execute(sa.text('SELECT * FROM products')).mappings():
        content = dict(row['metadata']) | {
            'title': row['title'], 'description': row['description'], 'provider': row['provider'],
            'providerOrganizationId': str(row['provider_organization_id']), 'theme': row['theme'],
            'modifiedAt': row['modified_at'].isoformat(), 'profileSnapshotId': None,
            'issuance': {'primaryDelivery': 'w3cVc', 'serviceAvailability': 'planned'}}
        checksum = hashlib.sha256(json.dumps(content, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()
        bind.execute(sa.text('''INSERT INTO drafts (id,product_id,content,revision,status,checksum,contributors,modified_at)
            VALUES (:id,:product,CAST(:content AS JSONB),1,'draft',:checksum,CAST(:contributors AS JSONB),:modified)'''),
            dict(id=uuid4(), product=row['id'], content=json.dumps(content,ensure_ascii=False), checksum=checksum,
                 contributors=json.dumps(['legacy:unknown']), modified=row['modified_at']))
    op.execute('''CREATE FUNCTION prevent_snapshot_mutation() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN RAISE EXCEPTION 'Immutable record: %', TG_TABLE_NAME; END; $$''')
    for table in ('profile_snapshots', 'product_versions', 'reviews', 'audit_events', 'outbox_events'):
        op.execute(f'''CREATE TRIGGER immutable_{table} BEFORE UPDATE OR DELETE ON {table}
            FOR EACH ROW EXECUTE FUNCTION prevent_snapshot_mutation()''')


def downgrade():
    raise RuntimeError('Palauta testattu varmuuskopio; julkaisu- ja auditointihistoriaa ei poisteta automaattisesti')
