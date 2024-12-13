import pytest
from app import create_app
from app.models.user import User
from app.extensions import db

@pytest.fixture(scope='module')
def app():
    app = create_app('testing')  # Ensures 'testing' config is loaded
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function', autouse=True)
def setup_database(_db):
    """Ensure the User table exists before running tests."""
    _db.create_all()
    yield
    _db.session.rollback()
    _db.drop_all()

@pytest.fixture(scope='function')
def test_user(db_session):
    user = User(username="testuser", email="test@example.com")
    user.set_password("password123")
    db_session.add(user)
    db_session.commit()
    yield user
    db_session.delete(user)
    db_session.commit()
