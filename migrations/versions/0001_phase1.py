"""Initial phase 1 schema, including safe adoption of an existing database."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

revision = "0001_phase1"
down_revision = None
branch_labels = depends_on = None


def legacy_tables():
    metadata = sa.MetaData()
    products = sa.Table("products", metadata,
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.String(5000), nullable=False),
        sa.Column("provider", sa.String(200), nullable=False),
        sa.Column("theme", sa.String(100), nullable=False),
        sa.Column("metadata", pg.JSONB(), nullable=False),
        sa.Column("modified_at", sa.DateTime(timezone=True), nullable=False))
    for name in ("title", "provider", "theme"):
        sa.Index(f"ix_products_{name}", products.c[name])
    sa.Table("demo_initialization", metadata,
             sa.Column("name", sa.String(100), primary_key=True))
    return metadata


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing = set(inspector.get_table_names()) - {"alembic_version"}
    expected = legacy_tables()
    if not existing:
        expected.create_all(bind)
        return
    # Never stamp an unknown or partial schema merely because products exists.
    if existing != set(expected.tables):
        raise RuntimeError("Tuntematon vaiheen 1 rakenne; ei muutoksia. Tarkista taulut ja ota varmuuskopio.")
    for name, table in expected.tables.items():
        actual = {c["name"]: c for c in inspector.get_columns(name)}
        if set(actual) != set(table.columns.keys()):
            raise RuntimeError(f"Poikkeavat sarakkeet taulussa {name}; ei automaattista käyttöönottoa")
        for column in table.columns:
            found = actual[column.name]
            if (bind.dialect.type_compiler.process(found["type"]) != bind.dialect.type_compiler.process(column.type)
                    or found["nullable"] != column.nullable
                    or getattr(found["type"], "timezone", None) != getattr(column.type, "timezone", None)):
                raise RuntimeError(f"Poikkeava sarake {name}.{column.name}; ei automaattista käyttöönottoa")
        if inspector.get_pk_constraint(name)["constrained_columns"] != [c.name for c in table.primary_key]:
            raise RuntimeError(f"Poikkeava pääavain: {name}")
        if inspector.get_foreign_keys(name) or inspector.get_check_constraints(name) or inspector.get_unique_constraints(name):
            raise RuntimeError(f"Poikkeavat rajoitteet: {name}")
        indexes = {(i["name"], tuple(i["column_names"]), i["unique"]) for i in inspector.get_indexes(name)}
        required = {(i.name, tuple(c.name for c in i.columns), False) for i in table.indexes}
        if indexes != required:
            raise RuntimeError(f"Poikkeavat indeksit: {name}")
    # A pre-existing phase 1 schema is not a new fixture target, even if emptied.
    bind.execute(sa.text("INSERT INTO demo_initialization (name) VALUES ('phase-1-fixtures') ON CONFLICT (name) DO NOTHING"))
    # Existing data and timestamps are untouched. Alembic records revision in its transaction.


def downgrade():
    raise RuntimeError("Automaattinen downgrade voisi hävittää tietoja; palauta testattu varmuuskopio")
