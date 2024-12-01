import pytest
from app import create_app
from app.config import TestingConfig
from app.extensions import db as _db  # Ensure correct import

@pytest.fixture(scope='module')
def app():
    app = create_app('testing')  # Pass 'testing' as a string
    with app.app_context():
        _db.create_all()
    yield app
    with app.app_context():
        _db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db(app):
    with app.app_context():
        _db.create_all()
    yield _db
    with app.app_context():
        _db.drop_all()

@pytest.fixture
def session(db):
    db.session.begin_nested()
    yield db.session
    db.session.rollback()
