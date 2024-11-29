import sys
from pathlib import Path
import pytest
from app.models.user import User
from app.extensions import db as _db
from flask_login import login_user
import re

# Get the project root directory
root = Path(__file__).resolve().parent.parent
sys.path.append(str(root))

from app import create_app

@pytest.fixture(scope='session')
def app():
    app = create_app('testing')
    with app.app_context():
        _db.create_all()
    return app

@pytest.fixture(scope='function')
def db(app):
    with app.app_context():
        _db.create_all()
        yield _db  # Provide the database instance
        _db.session.remove()
        _db.drop_all()

@pytest.fixture(scope='function')
def client(app, db):
    with app.test_client() as client:
        yield client

@pytest.fixture(scope='function')
def admin_user(db):
    user = User(username='admin', email='admin@example.com', is_admin=True)
    user.set_password('password')
    db.session.add(user)
    db.session.commit()
    yield user
    # Cleanup is handled by db.drop_all()

@pytest.fixture(scope='function')
def logged_in_client(app, admin_user):
    with app.test_client() as client:
        # Retrieve the login page to get the CSRF token
        response = client.get('/login')
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        
        # Extract the CSRF token from the form
        csrf_match = re.search(r'name="csrf_token" type="hidden" value="([^"]+)"', html)
        if not csrf_match:
            raise ValueError("CSRF token not found in login form")
        csrf_token = csrf_match.group(1)
        
        # Simulate logging in by making a POST request to the login endpoint with CSRF token
        response = client.post('/login', data={
            'username': admin_user.username,
            'password': 'password',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        assert response.status_code == 200
        yield client
