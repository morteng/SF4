import os
from flask import Flask, current_app
from sqlalchemy import create_engine
from alembic import context
from logging.config import fileConfig  # Import fileConfig for logging configuration
from app.models import db  # Import the db instance from your application models

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = os.getenv('SQLALCHEMY_DATABASE_URI')
    context.configure(
        url=url,
        target_metadata=db.metadata,  # Use db.metadata directly
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
    from app import create_app  # Import create_app here
    config_name = os.getenv('FLASK_CONFIG', 'development')
    app = create_app(config_name)
    with app.app_context():
        # Ensure the database directory exists
        db_path = os.path.dirname(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', ''))
        if not os.path.exists(db_path):
            os.makedirs(db_path)

        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

        with engine.connect() as connection:
            context.configure(
                connection=connection, target_metadata=db.metadata  # Use db.metadata directly
            )

            with context.begin_transaction():
                context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
