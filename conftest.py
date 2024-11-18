import pytest
from app import create_app, db

@pytest.fixture(scope='module')
def test_client():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()
