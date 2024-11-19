"""Alembic Environment Configuration

This file is used by Alembic to configure and script the migration environment.

It configures the context with just a URL and not an Engine, though an Engine is
acceptable here as well.  By skipping the Engine creation we don't even need a DBAPI
to be available.

Calls to context.execute() here emit the given string to the
script output.

Usage via the $ENV command line parameter:

    ENV=production alembic upgrade head

or, using the shorter version:

    ENV=p alembic upgrade head

Environment variables:

    SQLALCHEMY_DATABASE_URI - database URL for migrations

"""
import os
from logging.config import fileConfig
from alembic import context  # Import the context object from Alembic

from flask import current_app
from sqlalchemy import engine_from_config, pool

from app import create_app  # Import the create_app function from your application

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
from app.models import db  # Import the db instance from your application

target_metadata = db.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Load the Flask app configuration
    config_name = os.getenv('FLASK_CONFIG', 'development')
    app = create_app(config_name)
    with app.app_context():
        connectable = engine_from_config(
            config.get_section(config.config_ini_section),
            prefix='sqlalchemy.',
            poolclass=pool.NullPool,
        )

        with connectable.connect() as connection:
            context.configure(
                connection=connection, target_metadata=target_metadata
            )

            with context.begin_transaction():
                context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
