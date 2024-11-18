import pytest
from flask import Flask
from app import create_app
from app.models.user import User
from werkzeug.security import generate_password_hash

@pytest.fixture(scope='module')
def test_client():
    app = create_app('testing')
    with app.test_client() as client:
        yield client

@pytest.fixture(scope='module')
def admin_user(test_client):
    # Create an admin user if it doesn't exist
    from app.extensions import db
    with test_client.application.app_context():
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                password_hash=generate_password_hash('password'),
                email='admin@example.com',
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
        return admin

@pytest.fixture(scope='module')
def admin_token(test_client, admin_user):
    # Log in the admin user and get the token
    response = test_client.post('/admin/login', data={
        'username': admin_user.username,
        'password': 'password'
    }, follow_redirects=True)
    assert response.status_code == 200
    # Assuming the login returns a token in the session or cookies
    return response.headers.get('Authorization') or response.cookies['session']
