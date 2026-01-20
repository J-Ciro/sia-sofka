"""Alembic environment for migrations.

Uses DATABASE_URL_SYNC or DATABASE_URL (converted from async) for running migrations.
"""

import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# Alembic Config
config = context.config

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Override sqlalchemy.url from environment
url = os.getenv("DATABASE_URL_SYNC") or os.getenv("DATABASE_URL", "")
if "+asyncpg" in url:
    url = url.replace("+asyncpg", "")
if "+aiosqlite" in url:
    url = url.replace("+aiosqlite", "")
if url:
    config.set_main_option("sqlalchemy.url", url)

# Import Base and all models so target_metadata includes every table
from app.core.database import Base
from app.models import (  # noqa: F401
    User,
    Subject,
    Enrollment,
    Grade,
    ClaseSession,
    Attendance,
    AttendanceStats,
    AttendanceAlert,
    Classroom,
    Schedule,
)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
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
