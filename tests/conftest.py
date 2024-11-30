import sys
from pathlib import Path
import pytest
from app import create_app
from app.extensions import db as _db
from app.models.user import User

@pytest.fixture(scope='module')
def app():
    app = create_app('testing')
    with app.app_context():
        _db.create_all()
    yield app
    with app.app_context():
        _db.drop_all()

@pytest.fixture(scope='function')
def db(app):
    with app.app_context():
        _db.session.remove()
        _db.drop_all()
        _db.create_all()
        # Create admin user for each test function
        admin_user = User(
            username='admin_user',
            email='admin@example.com',
            is_admin=True
        )
        admin_user.set_password('password')  # Ensure password is set correctly
        _db.session.add(admin_user)
        _db.session.commit()
    yield _db
    with app.app_context():
        _db.session.remove()
        _db.drop_all()

@pytest.fixture(scope='function')
def client(app, db):
    with app.test_client() as client:
        yield client

@pytest.fixture(scope='function')
def logged_in_client(app, db):
    # Create a test client
    client = app.test_client()

    # Use the pre-existing admin user from the db fixture
    with app.app_context():
        admin_user = User.query.filter_by(email='admin@example.com').first()
        if not admin_user:
            raise ValueError("Admin user not found")

    # Log in the admin user with form data
    login_data = {
        'username': admin_user.username,
        'password': 'password'  # Ensure this matches the password set in db fixture
    }
    with app.app_context():
        response = client.post('/login', data=login_data, follow_redirects=True)
        assert response.status_code == 200

    return client
