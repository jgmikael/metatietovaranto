"""Run all migrations in one PostgreSQL transaction, serializing concurrent starts."""
from pathlib import Path
from alembic import command
from alembic.config import Config


def upgrade_database(engine, revision="head"):
    config = Config(str(Path(__file__).resolve().parents[2] / "alembic.ini"))
    with engine.begin() as connection:
        connection.exec_driver_sql("SELECT pg_advisory_xact_lock(17294002)")
        config.attributes["connection"] = connection
        command.upgrade(config, revision)
