import pytest
from app import create_app
from app.models.user import User

@pytest.fixture(scope='module')
def client():
    app = create_app('testing')
    with app.test_client() as client:
        yield client

@pytest.fixture(scope='module')
def session(client):
    from app.extensions import db
    db.create_all()
    yield db.session
    db.drop_all()

def test_user_login(client, session):
    # Example test case for user login
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Welcome' in response.data

def test_user_profile(client, session):
    # Example test case for user profile
    response = client.get('/profile')
    assert response.status_code == 302  # Redirect to login if not authenticated
