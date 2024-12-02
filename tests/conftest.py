import pytest
from app.models.user import User
from flask import session
from app.extensions import db  # Import the db object
from app import create_app
import pytest_flask_sqlalchemy

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def authenticate_client(client):
    def _authenticate(user):
        with client:
            response = client.post(
                '/login',
                data={'username': user.username, 'password': 'test_password'}
            )
            assert response.status_code == 302
            return client
    return _authenticate

@pytest.fixture
def auth_client(authenticate_client, user):
    return authenticate_client(user)

@pytest.fixture
def admin_user():
    user = User(
        username='admin_test',
        email='admin_test@example.com',
        password='test_password',
        is_admin=True
    )
    db.session.add(user)
    db.session.commit()
    yield user
    db.session.delete(user)
    db.session.commit()

@pytest.fixture
def admin_auth_client(authenticate_client, admin_user):
    return authenticate_client(admin_user)

@pytest.fixture
def db(_db):
    return _db
