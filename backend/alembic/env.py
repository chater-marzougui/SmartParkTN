"""Alembic environment configuration."""
import os
from logging.config import fileConfig
from pathlib import Path

from dotenv import load_dotenv

# Load backend/.env so DATABASE_URL is available without setting it manually
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from sqlalchemy import create_engine, pool
from alembic import context

# Load all models so Alembic can detect them
from app.models import Base  # noqa: F401 — registers all models

config = context.config

# Resolve DB URL: env var takes priority over alembic.ini placeholder
db_url = os.environ.get("DATABASE_URL") or config.get_main_option("sqlalchemy.url")
config.set_main_option("sqlalchemy.url", db_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
