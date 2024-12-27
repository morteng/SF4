import pytest
import logging
from datetime import datetime
from flask import url_for
from app.services.user_service import get_all_users
from flask_login import current_user
from app.models.user import User
from app.models.audit_log import AuditLog
from tests.conftest import extract_csrf_token, logged_in_admin, db_session
from app.constants import FlashMessages, FlashCategory
from werkzeug.security import generate_password_hash
from tests.utils import assert_flash_message, create_user_data
from app.utils import validate_password_strength
from app import db

@pytest.fixture(scope='function')
def user_data():
    logging.info("Creating user test data")
    return {
        'email': 'test@example.com',
        'password': 'StrongPass123!',  # Meets all password requirements
        'username': 'testuser',
        'csrf_token': 'test-csrf-token'  # Add CSRF token to test data
    }

@pytest.fixture
def client(app):
    ctx = app.test_request_context()
    ctx.push()
    client = app.test_client()
    with client.session_transaction() as session:
        session['csrf_token'] = 'test-csrf-token'
    yield client
    ctx.pop()

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

def verify_user_crud_operations(test_client, admin_user, test_data):
    """Verify full CRUD operations for users"""
    # Create
    response = test_client.post('/admin/users/create', 
                              data=test_data,
                              follow_redirects=True)
    assert response.status_code == 200
    assert FlashMessages.CREATE_USER_SUCCESS.value.encode() in response.data
    
    # Verify audit log
    log = AuditLog.query.filter_by(
        object_type='User',
        action='create_user'
    ).first()
    assert log is not None
    assert log.user_id == admin_user.id
    assert log.ip_address is not None
    
    # Read 
    response = test_client.get('/admin/users')
    assert response.status_code == 200
    assert test_data['username'].encode() in response.data
    
    # Update
    updated_data = test_data.copy()
    updated_data['username'] = 'updateduser'
    response = test_client.post('/admin/users/1/edit',
                              data=updated_data,
                              follow_redirects=True)
    assert response.status_code == 200
    assert FlashMessages.UPDATE_USER_SUCCESS.value.encode() in response.data
    
    # Verify audit log
    log = AuditLog.query.filter_by(
        object_type='User',
        action='update_user'
    ).first()
    assert log is not None
    
    # Delete
    response = test_client.post('/admin/users/1/delete',
                              follow_redirects=True)
    assert response.status_code == 200
    assert FlashMessages.DELETE_USER_SUCCESS.value.encode() in response.data
    
    # Verify audit log
    log = AuditLog.query.filter_by(
        object_type='User',
        action='delete_user'
    ).first()
    assert log is not None

def test_user_crud_operations(logged_in_admin, user_data, test_user):
    """Test full CRUD operations for users"""
    verify_user_crud_operations(logged_in_admin, test_user, user_data)

def test_get_all_users_sorting(db_session):
    """Test sorting functionality in get_all_users()"""
    # Create test users with password hashes
    user1 = User(
        username='user1',
        email='user1@example.com',
        created_at=datetime(2024, 1, 1),
        password_hash='hash1'
    )
    user2 = User(
        username='user2',
        email='user2@example.com',
        created_at=datetime(2024, 1, 2),
        password_hash='hash2'
    )
    user3 = User(
        username='user3',
        email='user3@example.com',
        created_at=datetime(2024, 1, 3),
        password_hash='hash3'
    )
    db_session.add_all([user1, user2, user3])
    db_session.commit()

    # Test username ascending
    result = get_all_users(sort_by='username', sort_order='asc')
    assert [u.username for u in result.items] == ['user1', 'user2', 'user3']

    # Test username descending
    result = get_all_users(sort_by='username', sort_order='desc')
    assert [u.username for u in result.items] == ['user3', 'user2', 'user1']

    # Test email ascending
    result = get_all_users(sort_by='email', sort_order='asc')
    assert [u.email for u in result.items] == ['user1@example.com', 'user2@example.com', 'user3@example.com']

    # Test created_at descending (default)
    result = get_all_users()
    assert [u.username for u in result.items] == ['user3', 'user2', 'user1']

def test_create_user_route(logged_in_admin, user_data, db_session):
    """Test user creation with proper CSRF and audit logging"""
    # Verify initial user count
    initial_count = User.query.count()
    
    # Test GET request
    create_response = logged_in_admin.get(url_for('admin.user.create'))
    assert create_response.status_code == 200
    
    # Verify CSRF token is present
    csrf_token = extract_csrf_token(create_response.data)
    assert csrf_token is not None
    
    # Test POST request
    response = logged_in_admin.post(url_for('admin.user.create'), data={
        'username': user_data['username'],
        'email': user_data['email'],
        'password': user_data['password'],
        'is_admin': False,
        'csrf_token': csrf_token
    }, follow_redirects=True)
    
    # Verify response
    assert response.status_code == 200
    assert FlashMessages.CREATE_USER_SUCCESS.value.encode() in response.data
    
    # Verify user creation
    assert User.query.count() == initial_count + 1
    created_user = User.query.filter_by(username=user_data['username']).first()
    assert created_user is not None
    assert created_user.email == user_data['email']
    
    # Verify audit log
    audit_log = AuditLog.query.filter_by(
        action='create_user',
        object_type='User',
        object_id=created_user.id
    ).first()
    assert audit_log is not None
    assert audit_log.details == f'Created user {user_data["username"]}'
    assert audit_log.ip_address is not None
    
    # Verify notification badge
    assert b'notification-badge' in response.data
    # Test GET request
    create_response = logged_in_admin.get(url_for('admin.user.create'))
    assert create_response.status_code == 200
    
    # Verify CSRF token is present
    csrf_token = extract_csrf_token(create_response.data)
    assert csrf_token is not None
    
    # Test POST request
    response = logged_in_admin.post(url_for('admin.user.create'), data={
        'username': user_data['username'],
        'email': user_data['email'],
        'password': user_data['password'],
        'is_admin': False,
        'csrf_token': csrf_token
    }, follow_redirects=True)
    
    # Verify response
    assert response.status_code == 200
    assert FlashMessages.CREATE_USER_SUCCESS.value.encode() in response.data
    
    # Verify user creation
    created_user = User.query.filter_by(username=user_data['username']).first()
    assert created_user is not None
    assert created_user.email == user_data['email']
    
    # Verify audit log
    audit_log = AuditLog.query.filter_by(
        action='create_user',
        object_type='User',
        object_id=created_user.id
    ).first()
    assert audit_log is not None
    assert audit_log.details == f'Created user {user_data["username"]}'
    assert audit_log.ip_address is not None
    
    # Verify audit log
    audit_log = AuditLog.query.filter_by(
        action='create_user',
        object_type='User',
        object_id=created_user.id
    ).first()
    assert audit_log is not None
    assert audit_log.details == f'Created user {user_data["username"]}'
    assert audit_log.ip_address is not None
    assert FlashMessages.CREATE_USER_SUCCESS.value.encode() in response.data
    
    # Verify user creation
    created_user = User.query.filter_by(username=user_data['username']).first()
    assert created_user is not None
    assert created_user.email == user_data['email']
    
    # Verify audit log
    audit_log = AuditLog.query.filter_by(
        action='create_user',
        object_type='User',
        object_id=created_user.id
    ).first()
    assert audit_log is not None
    assert audit_log.details == f'Created user {user_data["username"]}'
    assert audit_log.ip_address is not None
    
    # Verify notification badge
    assert b'notification-badge' in response.data

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
