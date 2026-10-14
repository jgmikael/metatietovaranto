"""Add organizations and one unambiguous provider reference per product."""
from uuid import NAMESPACE_URL, uuid5
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

revision = "0002_organizations"
down_revision = "0001_phase1"
branch_labels = depends_on = None


def upgrade():
    organizations = op.create_table("organizations",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("legal_name", sa.String(200), nullable=False),
        sa.Column("country", sa.String(2), nullable=False),
        sa.Column("identifiers", pg.JSONB(), nullable=False),
        sa.Column("synthetic", sa.Boolean(), nullable=False),
        sa.Column("legacy_product_id", pg.UUID(as_uuid=True), unique=True))
    op.add_column("products", sa.Column("provider_organization_id", pg.UUID(as_uuid=True), nullable=True))
    bind = op.get_bind()
    rows = bind.execute(sa.text('SELECT id, provider, metadata FROM products')).mappings()
    for product in rows:
        # A shared name is not an identity. Preserve one organization per legacy product.
        organization_id = uuid5(NAMESPACE_URL, f"https://example.org/metatietovaranto/legacy-provider/{product['id']}")
        bind.execute(organizations.insert().values(
            id=organization_id, legal_name=product["provider"], country="ZZ", identifiers=[],
            synthetic=product["metadata"].get("synthetic") is True, legacy_product_id=product["id"]))
        bind.execute(sa.text('UPDATE products SET provider_organization_id=:organization WHERE id=:product'),
                     {"organization": organization_id, "product": product["id"]})
    op.alter_column("products", "provider_organization_id", nullable=False)
    op.create_foreign_key("fk_products_provider_organization", "products", "organizations",
                          ["provider_organization_id"], ["id"], ondelete="RESTRICT")
    op.create_index("ix_products_provider_organization_id", "products", ["provider_organization_id"])
    # An unmarked, populated legacy database is existing user data, never a fresh fixture target.
    bind.execute(sa.text("""INSERT INTO demo_initialization (name)
        SELECT 'phase-1-fixtures' WHERE EXISTS (SELECT 1 FROM products)
        ON CONFLICT (name) DO NOTHING"""))


def downgrade():
    raise RuntimeError("Automaattinen downgrade voisi hävittää organisaatioiden viitteet; palauta varmuuskopio")
