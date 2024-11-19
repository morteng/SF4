import pytest
from app import create_app, db
from app.models.user import User
import logging

@pytest.fixture(scope='module')
def test_client():
    app = create_app('testing')
    with app.test_client() as client:
        with app.app_context():  # Ensure application context is pushed
            yield client

@pytest.fixture(scope='module')
def admin_user(test_client):
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        admin = User(username='admin', email='admin@example.com', is_admin=True)
        admin.set_password('password')
        db.session.add(admin)
        db.session.commit()
        yield admin
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='module')
def admin_token(test_client, admin_user):
    response = test_client.post('/users/login', data={  # Updated URL to match blueprint registration
        'username': admin_user.username,
        'password': 'password'
    }, follow_redirects=True)
    logging.info(f"Login response status code: {response.status_code}")
    assert response.status_code == 200
    return response.headers['Set-Cookie']
