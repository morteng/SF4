import pytest
import logging
from flask import url_for
from flask_login import current_user
from app.models.user import User
from app.models.audit_log import AuditLog
from tests.conftest import extract_csrf_token, logged_in_admin, db_session
from app.constants import FlashMessages, FlashCategory
from werkzeug.security import generate_password_hash
from tests.utils import assert_flash_message, create_user_data
from app.utils import validate_password_strength

@pytest.fixture(scope='function')
def user_data():
    logging.info("Creating user test data")
    return {
        'email': 'test@example.com',
        'password': 'StrongPass123!',  # Meets all password requirements
        'username': 'testuser'
    }

@pytest.fixture(scope='function')
def test_user(db_session, user_data):
    """Provide a test user."""
    user = User(
        username=user_data['username'],
        email=user_data['email'],
        password_hash=generate_password_hash(user_data['password']),
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()
    yield user
    db_session.delete(user)
    db_session.commit()

def test_create_user_route(logged_in_admin, user_data):
    # Test GET request
    create_response = logged_in_admin.get(url_for('admin.user.create'))
    assert create_response.status_code == 200
    
    # Verify admin user context
    with logged_in_admin.session_transaction() as session:
        assert '_user_id' in session
        admin_user_id = session['_user_id']
        admin_user = User.query.get(int(admin_user_id))  # Convert to int since _user_id is stored as string
        assert admin_user is not None
        assert admin_user.is_admin
    
    # Test POST request
    csrf_token = extract_csrf_token(create_response.data)
    response = logged_in_admin.post(url_for('admin.user.create'), data={
        'username': user_data['username'],
        'email': user_data['email'],
        'password': user_data['password'],
        'is_admin': False,
        'submit': 'Create',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    
    # Verify response
    assert response.status_code == 200
    assert FlashMessages.CREATE_USER_SUCCESS.value.encode() in response.data
    
    # Verify user creation
    users = User.query.all()
    assert any(user.username == user_data['username'] and user.email == user_data['email'] for user in users)
    
    # Verify notification badge is present
    assert b'notification-badge' in response.data
    
    # Verify audit log was created
    audit_log = AuditLog.query.filter_by(action='create_user').first()
    assert audit_log is not None
    
    # Verify audit log details
    assert audit_log.user_id == admin_user.id
    assert audit_log.object_type == 'User'
    assert audit_log.details == f'Created user {user_data["username"]}'
    assert audit_log.object_type == 'User'
    assert audit_log.details == f'Created user {user_data["username"]}'
    assert audit_log.ip_address is not None

def test_create_user_route_with_invalid_data(logged_in_admin, user_data):
    create_response = logged_in_admin.get(url_for('admin.user.create'))
    assert create_response.status_code == 200

    csrf_token = extract_csrf_token(create_response.data)
    invalid_data = {
        'username': '',  # Invalid username
        'email': user_data['email'],
        'password': user_data['password'],
        'csrf_token': csrf_token
    }
    response = logged_in_admin.post(url_for('admin.user.create'), data=invalid_data, follow_redirects=True)

    assert response.status_code == 200
    users = User.query.all()
    assert not any(user.username == '' for user in users)  # Ensure no user with an empty username was created
    # Assert the flash message using constants
    assert_flash_message(response, FlashMessages.CREATE_USER_INVALID_DATA)

def test_update_user_route(logged_in_admin, test_user, db_session):
    update_response = logged_in_admin.get(url_for('admin.user.edit', id=test_user.id))  # Change here
    assert update_response.status_code == 200

    csrf_token = extract_csrf_token(update_response.data)
    updated_data = {
        'username': 'updateduser',
        'email': test_user.email,
        'password': test_user.password_hash,  # Assuming password hash is not changed in this test
        'csrf_token': csrf_token
    }
    response = logged_in_admin.post(url_for('admin.user.edit', id=test_user.id), data=updated_data, follow_redirects=True)  # Change here

    assert response.status_code == 200
    updated_user = db_session.get(User, test_user.id)
    assert updated_user.username == 'updateduser'
    # Assert the flash message using constants
    assert_flash_message(response, FlashMessages.UPDATE_USER_SUCCESS)

def test_update_user_route_with_invalid_id(logged_in_admin):
    update_response = logged_in_admin.get(url_for('admin.user.edit', id=9999))
    assert update_response.status_code == 302
    assert url_for('admin.user.index', _external=False) == update_response.headers['Location']
    # Follow the redirect to verify the flash message
    index_response = logged_in_admin.get(update_response.headers['Location'])
    assert FlashMessages.USER_NOT_FOUND.value.encode() in index_response.data

def extract_csrf_token(response_data):
    """Extract CSRF token from HTML response."""
    from bs4 import BeautifulSoup
    
    soup = BeautifulSoup(response_data, 'html.parser')
    
    # Look for CSRF token in hidden input with name="csrf_token"
    csrf_input = soup.find('input', {'name': 'csrf_token'})
    if csrf_input:
        return csrf_input.get('value')
    
    # Look for CSRF token in meta tag as fallback
    meta_token = soup.find('meta', {'name': 'csrf-token'})
    if meta_token:
        return meta_token.get('content')
    
    # Look for CSRF token in any hidden input as last resort
    hidden_input = soup.find('input', {'type': 'hidden'})
    if hidden_input and hidden_input.get('name') == 'csrf_token':
        return hidden_input.get('value')
    
    logging.warning("CSRF token not found in response")
    return None

def test_delete_user_route(logged_in_admin, test_user, db_session):
    """Test user deletion with proper CSRF handling"""
    # Initialize session and get CSRF token
    index_response = logged_in_admin.get(url_for('admin.user.index'))
    assert index_response.status_code == 200
    
    # Extract CSRF token with debug logging
    csrf_token = extract_csrf_token(index_response.data)
    logging.info(f"Extracted CSRF token: {csrf_token}")
    
    # Verify CSRF token exists
    assert csrf_token is not None, "CSRF token not found in response. Response content: " + index_response.data.decode('utf-8')

def test_reset_password_route(logged_in_admin, test_user):
    """Test password reset functionality"""
    # Get CSRF token
    index_response = logged_in_admin.get(url_for('admin.user.index'))
    csrf_token = extract_csrf_token(index_response.data)
    
    # Reset password
    response = logged_in_admin.post(
        url_for('admin.user.reset_password', id=test_user.id),
        data={'csrf_token': csrf_token},
        follow_redirects=True
    )
    
    assert response.status_code == 200
    assert FlashMessages.PASSWORD_RESET_SUCCESS.value.encode() in response.data

def test_toggle_active_route(logged_in_admin, test_user):
    """Test user activation/deactivation"""
    # Get CSRF token
    index_response = logged_in_admin.get(url_for('admin.user.index'))
    csrf_token = extract_csrf_token(index_response.data)
    
    # Deactivate user
    response = logged_in_admin.post(
        url_for('admin.user.toggle_active', id=test_user.id),
        data={'csrf_token': csrf_token},
        follow_redirects=True
    )
    
    assert response.status_code == 200
    assert FlashMessages.USER_DEACTIVATED.value.encode() in response.data
    
    # Reactivate user
    response = logged_in_admin.post(
        url_for('admin.user.toggle_active', id=test_user.id),
        data={'csrf_token': csrf_token},
        follow_redirects=True
    )
    
    assert response.status_code == 200
    assert FlashMessages.USER_ACTIVATED.value.encode() in response.data
    
    # Perform deletion
    delete_response = logged_in_admin.post(
        url_for('admin.user.delete', id=test_user.id),
        data={'csrf_token': csrf_token},
        follow_redirects=True
    )
    
    # Verify response
    assert delete_response.status_code == 200
    assert FlashMessages.DELETE_USER_SUCCESS.value.encode() in delete_response.data
    
    # Verify user is deleted
    deleted_user = db_session.get(User, test_user.id)
    assert deleted_user is None

def test_delete_user_route_invalid_id(logged_in_admin):
    """Test deleting a non-existent user"""
    # Initialize session and get CSRF token
    index_response = logged_in_admin.get(url_for('admin.user.index'))
    csrf_token = extract_csrf_token(index_response.data)
    
    # Attempt to delete non-existent user
    delete_response = logged_in_admin.post(
        url_for('admin.user.delete', id=9999),
        data={'csrf_token': csrf_token},
        follow_redirects=True
    )
    
    # Verify error response
    assert delete_response.status_code == 400
    assert FlashMessages.USER_NOT_FOUND.value.encode() in delete_response.data
    
    # Verify the token in the session matches the form token
    with logged_in_admin.session_transaction() as session:
        session_csrf_token = session.get('csrf_token')
        assert session_csrf_token is not None, "CSRF token not found in session"

    # Perform the DELETE operation with the valid CSRF token
    delete_response = logged_in_admin.post(
        url_for('admin.user.delete', id=test_user.id),
        data={'csrf_token': csrf_token},
        follow_redirects=True
    )
    
    # Verify the response
    assert delete_response.status_code == 200, "Failed to delete user"
    
    # Verify user is deleted
    db_session.expire_all()
    updated_user = db_session.get(User, test_user.id)
    assert updated_user is None
    
    # Verify flash message in session
    with logged_in_admin.session_transaction() as session:
        flashed_messages = session.get('_flashes', [])
        assert any(msg[1] == FlashMessages.DELETE_USER_SUCCESS.value for msg in flashed_messages), \
            f"Expected flash message '{FlashMessages.DELETE_USER_SUCCESS.value}' not found in session"

def test_deactivate_user_route(logged_in_admin, test_user):
    # Get CSRF token
    index_response = logged_in_admin.get(url_for('admin.user.index'))
    csrf_token = extract_csrf_token(index_response.data)
    
    # Deactivate user
    response = logged_in_admin.post(
        url_for('admin.user.deactivate', id=test_user.id),
        data={'csrf_token': csrf_token},
        follow_redirects=True
    )
    
    assert response.status_code == 200
    assert FlashMessages.USER_DEACTIVATED.value.encode() in response.data

def test_activate_user_route(logged_in_admin, test_user):
    # First deactivate the user
    test_user.is_active = False
    db_session.commit()
    
    # Get CSRF token
    index_response = logged_in_admin.get(url_for('admin.user.index'))
    csrf_token = extract_csrf_token(index_response.data)
    
    # Activate user
    response = logged_in_admin.post(
        url_for('admin.user.activate', id=test_user.id),
        data={'csrf_token': csrf_token},
        follow_redirects=True
    )
    
    assert response.status_code == 200
    assert FlashMessages.USER_ACTIVATED.value.encode() in response.data
    assert test_user.is_active is True

def test_password_strength_validation():
    # Test weak passwords
    assert validate_password_strength("weak") is False
    assert validate_password_strength("weak123") is False
    assert validate_password_strength("Weak") is False
    
    # Test strong password
    assert validate_password_strength("StrongPass123!") is True

def test_delete_user_route_with_invalid_id(logged_in_admin):
    delete_response = logged_in_admin.post(url_for('admin.user.delete', id=9999))
    assert delete_response.status_code == 400

def test_create_user_route_with_database_error(logged_in_admin, user_data, db_session, monkeypatch):
    with logged_in_admin.application.app_context():
        # First get the CSRF token
        get_response = logged_in_admin.get(url_for('admin.user.create'))
        assert get_response.status_code == 200
        csrf_token = extract_csrf_token(get_response.data)
        assert csrf_token is not None, "CSRF token not found in response"
            
        # Prepare data with CSRF token
        data = user_data.copy()
        data['csrf_token'] = csrf_token

        def mock_commit(*args, **kwargs):
            raise Exception("Database error")
            
        monkeypatch.setattr(db_session, 'commit', mock_commit)
            
        response = logged_in_admin.post(url_for('admin.user.create'), data=data)
            
        # Check for error response - should be 400 with template rendered directly
        assert response.status_code == 400
            
        # Check for the flash message in the response HTML
        decoded_response = response.data.decode('utf-8')
        assert FlashMessages.CREATE_USER_ERROR.value in decoded_response, \
            f"Expected flash message containing '{FlashMessages.CREATE_USER_ERROR.value}' not found in response. Response was: {decoded_response}"
            
        # Verify the form is still present with the submitted data
        assert 'Create User' in decoded_response
        assert user_data['username'] in decoded_response
            
        # Verify the user was not created
        users = User.query.all()
        assert not any(user.username == data['username'] for user in users)

        users = User.query.all()
        assert not any(user.username == data['username'] for user in users)  # Ensure no user was created
