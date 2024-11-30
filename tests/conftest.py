import sys
from pathlib import Path

# Add the root directory of the project to the PYTHONPATH
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

import pytest
from app import create_app
from app.extensions import db as _db
from app.models.user import User

@pytest.fixture(scope='module')
def app():
    app = create_app('testing')
    with app.app_context():
        _db.create_all()
        # Initialize admin user
        admin_user = _db.session.query(User).filter_by(email='admin@example.com').first()
        if not admin_user:
            admin_user = User(
                username='admin_user',
                password_hash='pbkdf2:sha256:150000$XbL3IjWn$3d8Kq7J29e4gFyhiuQlZIl12tXcVU8S2R5Qx5hPZV0k=',
                email='admin@example.com',
                is_admin=True
            )
            _db.session.add(admin_user)
            _db.session.commit()
    yield app
    with app.app_context():
        _db.drop_all()

@pytest.fixture(scope='function')
def db(app):
    with app.app_context():
        _db.create_all()
        yield _db
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

    # Create an admin user
    admin_user = User(username='admin', email='admin@example.com', is_admin=True)
    admin_user.set_password('password')
    db.session.add(admin_user)
    db.session.commit()

    # Log in the admin user with form data
    login_data = {
        'username': 'admin',
        'password': 'password'
    }
    response = client.post('/login', data=login_data, follow_redirects=True)
    assert response.status_code == 200

    return client
