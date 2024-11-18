from flask import Flask
from app import create_app, db  # Ensure db is imported here

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
