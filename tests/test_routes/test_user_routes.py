import pytest
from app import create_app, db
from app.models.user import User

@pytest.fixture(scope='module')
def test_client():
    app = create_app('testing')
    with app.test_client() as client:
        yield client

@pytest.fixture(scope='module')
def init_database(test_client):
    db.create_all()
    user = User(username='testuser', password_hash='hashed_password', email='test@example.com', is_admin=False)
    db.session.add(user)
    db.session.commit()

def test_user_index(test_client, init_database):
    response = test_client.get('/user/index')
    assert response.status_code == 200
    assert b'testuser' in response.data

def test_user_profile(test_client, init_database):
    response = test_client.get('/user/profile/1')
    assert response.status_code == 200
    assert b'testuser' in response.data

def test_register_user(test_client, init_database):
    response = test_client.post('/register', json={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'secure_password'
    })
    assert response.status_code == 201
    assert b'You\'re all set!' in response.data

def test_register_user_missing_fields(test_client, init_database):
    response = test_client.post('/register', json={
        'username': 'newuser',
        'email': 'newuser@example.com'
    })
    assert response.status_code == 400
    assert b'Missing required fields' in response.data

def test_register_user_existing_username(test_client, init_database):
    response = test_client.post('/register', json={
        'username': 'testuser',
        'email': 'newuser@example.com',
        'password': 'secure_password'
    })
    assert response.status_code == 409
    assert b'User already exists' in response.data

def test_register_user_existing_email(test_client, init_database):
    response = test_client.post('/register', json={
        'username': 'newuser',
        'email': 'test@example.com',
        'password': 'secure_password'
    })
    assert response.status_code == 409
    assert b'User already exists' in response.data

def test_update_user(test_client, init_database):
    user = User.query.filter_by(username='testuser').first()
    response = test_client.put(f'/users/{user.id}', json={
        'username': 'updateduser',
        'email': 'updated@example.com',
        'password': 'new_secure_password'
    })
    assert response.status_code == 200
    assert b'User updated successfully' in response.data

def test_update_user_missing_data(test_client, init_database):
    user = User.query.filter_by(username='testuser').first()
    response = test_client.put(f'/users/{user.id}', json={})
    assert response.status_code == 400
    assert b'No data provided' in response.data

def test_update_user_nonexistent(test_client, init_database):
    response = test_client.put('/users/999', json={
        'username': 'updateduser',
        'email': 'updated@example.com',
        'password': 'new_secure_password'
    })
    assert response.status_code == 404
