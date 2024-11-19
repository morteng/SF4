import pytest
from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

@pytest.fixture(scope='module')
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='module')
def test_client(app):
    with app.test_client() as client:
        with app.app_context():
            yield client

@pytest.fixture(scope='module')
def admin_user(app, test_client):
    password_hash = generate_password_hash('password', method='sha256')
    with app.app_context():
        user = User(username='admin', password_hash=password_hash, email='admin@example.com', is_admin=True)
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture(scope='module')
def admin_token(test_client, admin_user):
    response = test_client.post('/users/login', data={
        'username': admin_user.username,
        'password': 'password'
    }, follow_redirects=True)
    assert response.status_code == 200
    return response.json.get('token') if response.json else None

@pytest.fixture(scope='module')
def user_token(test_client):
    response = test_client.post('/users/login', data={
        'username': 'user',
        'password': 'password'
    }, follow_redirects=True)
    assert response.status_code == 200
    return response.json.get('token') if response.json else None
