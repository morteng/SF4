# tests/conftest.py
import pytest
from app import create_app
from app.extensions import db  # Ensure db is imported from app.extensions

@pytest.fixture(scope='module')
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()  # Ensure db is initialized within the app context
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='module')
def client(app):
    return app.test_client()

@pytest.fixture(scope='module')
def runner(app):
    return app.test_cli_runner()
