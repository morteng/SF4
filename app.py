from flask import Flask
from app.extensions import db, migrate  # Ensure db and migrate are imported here
from app.models import Base  # Ensure Base is imported here
from app.config import get_config

def create_app(config_name):
    app = Flask(__name__)
    
    # Load configuration using the get_config function
    config = get_config(config_name)
    if config:
        app.config.from_object(config)
    else:
        raise ValueError(f"Unknown configuration name: {config_name}")
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Register blueprints and other components here if needed
    
    return app

def init_db(app):
    with app.app_context():
        try:
            db.create_all()
            print("Database initialized successfully.")
        except Exception as e:
            print(f"Failed to initialize database: {e}")

def run_migrations():
    from alembic import command
    from alembic.config import Config
    alembic_cfg = Config("alembic.ini")
    try:
        command.upgrade(alembic_cfg, "head")
        print("Migrations applied successfully.")
    except Exception as e:
        print(f"Failed to apply migrations: {e}")

def run_tests():
    import pytest
    pytest.main(['-v', 'tests'])

def main():
    app = create_app('development')
    init_db(app)
    run_migrations()
    try:
        app.run()
    except Exception as e:
        print(f"Application failed to start: {e}")

if __name__ == '__main__':
    main()
