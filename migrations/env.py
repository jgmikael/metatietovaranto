"""Use a caller-owned transaction for controlled, locked startup migrations."""
import os
from alembic import context
from sqlalchemy import create_engine
from apps.api.models import Base

config = context.config

def run(connection):
    context.configure(connection=connection, target_metadata=Base.metadata)
    with context.begin_transaction():
        context.run_migrations()

if context.is_offline_mode():
    raise RuntimeError("Migraatiot vaativat PostgreSQL-yhteyden; legacy-rakenne tarkistetaan tietokannasta")
connection = config.attributes.get("connection")
if connection is not None:
    run(connection)
else:
    engine = create_engine(os.environ["DATABASE_URL"])
    with engine.begin() as connection:
        connection.exec_driver_sql("SELECT pg_advisory_xact_lock(17294002)")
        run(connection)
