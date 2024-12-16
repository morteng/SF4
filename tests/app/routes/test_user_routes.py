import pytest
from flask import url_for
from app.models.user import User
from tests.conftest import extract_csrf_token
from app.extensions import db  # Import the db from extensions

@pytest.fixture(scope='function')
def test_user(db_session):
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    yield user

    # Teardown: Attempt to delete the user and rollback if an error occurs
    try:
        db_session.delete(user)
        db_session.commit()
    except Exception as e:
        print(f"Failed to delete test user during teardown: {e}")
        db_session.rollback()

@pytest.fixture(scope='function')
def admin_user(db_session):
    user = User(username='adminuser', email='admin@example.com', is_admin=True)
    user.set_password('password123')
    db_session.add(user)
    db_session.commit()
    yield user

    # Teardown: Attempt to delete the user and rollback if an error occurs
    try:
        db_session.delete(user)
        db_session.commit()
    except Exception as e:
        print(f"Failed to delete admin user during teardown: {e}")
        db_session.rollback()

@pytest.fixture(scope='function')
def db_session(app):
    with app.app_context():
        session = db.session  # Use the imported db object
        yield session
        session.rollback()

def test_profile_route(logged_in_client, test_user):
    profile_response = logged_in_client.get(url_for('user.profile'))
    assert profile_response.status_code == 200

def test_edit_profile_route(logged_in_client, test_user, db_session):
    edit_response = logged_in_client.get(url_for('user.edit_profile'))
    assert edit_response.status_code == 200

    csrf_token = extract_csrf_token(edit_response.data)
    response = logged_in_client.post(url_for('user.edit_profile'), data={
        'username': 'newusername',
        'email': 'newemail@example.com',
        'csrf_token': csrf_token
    }, follow_redirects=True)

    assert response.status_code == 200
    updated_user = db_session.get(User, test_user.id)  # Update this line to use db_session.get
    assert updated_user.username == 'newusername'
    assert updated_user.email == 'newemail@example.com'

def test_login_regular_user(logged_in_client, test_user):
    login_response = logged_in_client.get(url_for('user.login'))
    assert login_response.status_code == 200

    csrf_token = extract_csrf_token(login_response.data)
    response = logged_in_client.post(url_for('user.login'), data={
        'username': 'testuser',
        'password': 'password123',
        'csrf_token': csrf_token
    }, follow_redirects=True)

    assert response.status_code == 200
    assert url_for('user.profile') in response.request.url

def test_login_admin_user(logged_in_client, admin_user):
    login_response = logged_in_client.get(url_for('user.login'))
    assert login_response.status_code == 200

    csrf_token = extract_csrf_token(login_response.data)
    response = logged_in_client.post(url_for('user.login'), data={
        'username': 'adminuser',
        'password': 'password123',
        'csrf_token': csrf_token
    }, follow_redirects=True)

    assert response.status_code == 200
    assert url_for('admin.dashboard.dashboard') in response.request.url
