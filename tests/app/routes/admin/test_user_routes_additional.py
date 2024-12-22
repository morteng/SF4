import pytest
from flask import url_for
from app.forms.user_forms import ProfileForm, LoginForm
from app.models.user import User
from tests.conftest import extract_csrf_token, logged_in_client
from app.constants import FLASH_MESSAGES, FLASH_CATEGORY_SUCCESS, FLASH_CATEGORY_ERROR

@pytest.fixture(scope='function')
def user_data():
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    }

@pytest.fixture(scope='function')
def test_user(db_session, user_data):
    """Provide a test user."""
    user = User(
        username=user_data['username'],
        email=user_data['email']
    )
    user.set_password(user_data['password'])
    db_session.add(user)
    db_session.commit()
    yield user
    db_session.delete(user)
    db_session.commit()

def test_login_route(logged_in_client, user_data):
    login_response = logged_in_client.get(url_for('user.login'))
    assert login_response.status_code == 200

    csrf_token = extract_csrf_token(login_response.data)
    response = logged_in_client.post(url_for('user.login'), data={
        'username': user_data['username'],
        'password': user_data['password'],
        'csrf_token': csrf_token
    }, follow_redirects=True)

    assert response.status_code == 200
    # Assert the flash message using constants
    assert FLASH_MESSAGES["LOGIN_SUCCESS"].encode() in response.data

def test_login_route_with_invalid_credentials(logged_in_client, user_data):
    login_response = logged_in_client.get(url_for('user.login'))
    assert login_response.status_code == 200

    csrf_token = extract_csrf_token(login_response.data)
    invalid_data = {
        'username': user_data['username'],
        'password': 'wrongpassword',
        'csrf_token': csrf_token
    }
    response = logged_in_client.post(url_for('user.login'), data=invalid_data, follow_redirects=True)

    assert response.status_code == 200
    # Assert the flash message using constants
    assert any(FLASH_MESSAGES["LOGIN_INVALID_CREDENTIALS"].encode() in msg for msg in response.data.split(b'\n') if b'flash' in msg)

    # Ensure that the user is not redirected to a protected page
    assert b'Login' in response.data  # Check if login form is still present

def test_profile_route(logged_in_client):
    profile_response = logged_in_client.get(url_for('user.profile'))
    assert profile_response.status_code == 200

def test_edit_profile_route(logged_in_client, test_user):
    edit_response = logged_in_client.get(url_for('user.edit_profile'))
    assert edit_response.status_code == 200

    csrf_token = extract_csrf_token(edit_response.data)
    updated_data = {
        'username': 'updateduser',
        'email': test_user.email,
        'csrf_token': csrf_token
    }
    response = logged_in_client.post(url_for('user.edit_profile'), data=updated_data, follow_redirects=True)

    assert response.status_code == 200
    # Assert the flash message using constants
    assert FLASH_MESSAGES["PROFILE_UPDATE_SUCCESS"].encode() in response.data

def test_edit_profile_route_with_invalid_data(logged_in_client, test_user):
    edit_response = logged_in_client.get(url_for('user.edit_profile'))
    assert edit_response.status_code == 200

    csrf_token = extract_csrf_token(edit_response.data)
    invalid_data = {
        'username': '',  # Invalid username
        'email': test_user.email,
        'csrf_token': csrf_token
    }
    response = logged_in_client.post(url_for('user.edit_profile'), data=invalid_data, follow_redirects=True)

    assert response.status_code == 200
    # Assert the flash message using constants
    assert FLASH_MESSAGES["PROFILE_UPDATE_INVALID_DATA"].encode() in response.data

def test_edit_profile_route_with_duplicate_username(logged_in_client, test_user, db_session):
    # Create another user with a different username
    existing_user = User(username='existinguser', email='existing@example.com')
    existing_user.set_password('password123')
    db_session.add(existing_user)
    db_session.commit()

    edit_response = logged_in_client.get(url_for('user.edit_profile'))
    assert edit_response.status_code == 200

    csrf_token = extract_csrf_token(edit_response.data)
    duplicate_data = {
        'username': existing_user.username,  # Duplicate username
        'email': test_user.email,
        'csrf_token': csrf_token
    }
    response = logged_in_client.post(url_for('user.edit_profile'), data=duplicate_data, follow_redirects=True)

    assert response.status_code == 200
    # Assert the flash message using constants
    assert FLASH_MESSAGES["USERNAME_ALREADY_EXISTS"].encode() in response.data

    db_session.delete(existing_user)
    db_session.commit()
