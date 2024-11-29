import sys
import os

# Get the absolute path to the project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from app import create_app, db
from alembic.config import Config
from alembic import command
import pytest

@pytest.fixture(scope='module')
def app():
    app = create_app('testing')
    with app.app_context():
        # Run migrations
        alembic_cfg = Config("migrations/alembic.ini")  # Adjusted path to alembic.ini
        command.upgrade(alembic_cfg, "head")
        db.session.commit()
    yield app
    with app.app_context():
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()
