"""Server-side login sessions and explicit organization memberships."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

revision = "0003_auth"
down_revision = "0002_organizations"
branch_labels = depends_on = None


def upgrade():
    op.create_table("organization_memberships",
        sa.Column("subject", sa.String(255), primary_key=True),
        sa.Column("organization_id", pg.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), primary_key=True),
        sa.Column("role", sa.String(20), nullable=False))
    op.create_table("web_sessions",
        sa.Column("token_hash", sa.String(64), primary_key=True),
        sa.Column("subject", sa.String(255), nullable=False),
        sa.Column("username", sa.String(255), nullable=False),
        sa.Column("csrf_token", sa.String(64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_web_sessions_expires_at", "web_sessions", ["expires_at"])
    op.create_table("oauth_flows",
        sa.Column("state_hash", sa.String(64), primary_key=True),
        sa.Column("flow_hash", sa.String(64), nullable=False),
        sa.Column("verifier", sa.String(128), nullable=False),
        sa.Column("nonce", sa.String(128), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_oauth_flows_expires_at", "oauth_flows", ["expires_at"])


def downgrade():
    raise RuntimeError("Palauta testattu varmuuskopio; älä poista istuntoja ja jäsenyyksiä automaattisesti")
