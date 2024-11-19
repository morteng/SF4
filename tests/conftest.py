import pytest
from app import create_app, db

@pytest.fixture(scope='module')
def app():
    app = create_app('testing')
    return app

@pytest.fixture(scope='module')
def client(app):
    with app.test_client() as client:
        yield client

@pytest.fixture(scope='module')
def session(app):
    with app.app_context():
        db.create_all()
        yield db.session
        db.drop_all()
