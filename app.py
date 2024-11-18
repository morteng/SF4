from flask import Flask
from app import create_app, db  # Ensure db is imported here

def init_db(app):
    with app.app_context():
        db.create_all()

def run_migrations():
    from alembic import command
    from alembic.config import Config
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

def run_tests():
    import pytest
    pytest.main(['-v', 'tests'])

if __name__ == '__main__':
    main()
