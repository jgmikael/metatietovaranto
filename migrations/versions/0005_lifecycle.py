"""Append-only publication lifecycle events; never rewrite snapshots or old outbox rows."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

revision = '0005_lifecycle'
down_revision = '0004_publication'
branch_labels = depends_on = None


def upgrade():
    op.create_table('lifecycle_events',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True),
        sa.Column('version_id', pg.UUID(as_uuid=True), sa.ForeignKey('product_versions.id'), nullable=False),
        sa.Column('sequence', sa.Integer(), nullable=False),
        sa.Column('previous_status', sa.String(20), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('reason', sa.String(2000), nullable=False),
        sa.Column('replacement_version_id', pg.UUID(as_uuid=True), sa.ForeignKey('product_versions.id')),
        sa.Column('actor', sa.String(255), nullable=False),
        sa.Column('organization_id', pg.UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint('version_id', 'sequence'),
        sa.CheckConstraint('sequence > 0', name='ck_lifecycle_sequence'),
        sa.CheckConstraint("(previous_status = 'published' AND status IN ('deprecated','withdrawn')) OR (previous_status = 'deprecated' AND status = 'withdrawn')", name='ck_lifecycle_transition'),
        sa.CheckConstraint("replacement_version_id IS NULL OR (status = 'deprecated' AND replacement_version_id <> version_id)", name='ck_lifecycle_replacement'))
    op.create_table('lifecycle_outbox_events',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True),
        sa.Column('event_id', pg.UUID(as_uuid=True), sa.ForeignKey('lifecycle_events.id'), nullable=False, unique=True),
        sa.Column('payload', pg.JSONB(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False))
    for table in ('lifecycle_events', 'lifecycle_outbox_events'):
        op.execute(f'''CREATE TRIGGER immutable_{table} BEFORE UPDATE OR DELETE ON {table}
            FOR EACH ROW EXECUTE FUNCTION prevent_snapshot_mutation()''')


def downgrade():
    raise RuntimeError('Elinkaarihistoriaa ei poisteta automaattisesti; palauta testattu varmuuskopio erilliseen kantaan')
