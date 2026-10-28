import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine

from app import models
from app.database import Base, database_url

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Safe default: use the isolated migration test database.
# Override with QFORGE_ALEMBIC_DATABASE when explicitly needed.
target_database = os.getenv(
    "QFORGE_ALEMBIC_DATABASE",
    "qforge_ai_migration_test",
)
migration_url = database_url.set(database=target_database)


def run_migrations_offline() -> None:
    context.configure(
        url=migration_url.render_as_string(hide_password=True),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(migration_url, pool_pre_ping=True)

    try:
        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                compare_type=True,
            )

            with context.begin_transaction():
                context.run_migrations()
    finally:
        connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
