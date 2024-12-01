import pytest
from app import create_app
from app.extensions import db as _db
import app.models  # Ensure all models are imported

@pytest.fixture(scope='module')
def app():
    app = create_app('testing')
    with app.app_context():
        yield app

@pytest.fixture
def db(app):
    with app.app_context():
        _db.create_all()
        yield _db
        _db.drop_all()
