import pytest
import logging
import re
from datetime import datetime, UTC
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

import uuid

@pytest.fixture(scope='function')
def test_user(db_session):
    """Provide a test admin user with unique credentials."""
    # Clean up any existing test users
    db_session.query(User).filter(User.username.like('test_admin_%')).delete()
    
    # Create new test user with unique credentials
    user = User(
        username=f'test_admin_{uuid.uuid4().hex[:8]}',
        email=f'test_admin_{uuid.uuid4().hex[:8]}@example.com',
        password_hash=generate_password_hash('AdminPass123!'),
        is_admin=True
    )
    db_session.add(user)
    db_session.commit()
    yield user
        
    # Clean up - refresh user instance before deletion
    user = db_session.merge(user)
    db_session.delete(user)
    db_session.commit()
    db_session.commit()

def verify_user_crud_operations(test_client, admin_user, test_data):
    """Verify full CRUD operations for users"""
    # First get the CSRF token from the create form
    create_response = test_client.get('/admin/users/create')
    assert create_response.status_code == 200
    csrf_token = extract_csrf_token(create_response.data)
    assert csrf_token is not None
    
    # Add CSRF token to test data
    test_data['csrf_token'] = csrf_token
    
    # Create user
    response = test_client.post('/admin/users/create', 
                              data=test_data,
                              follow_redirects=True)
    
    # Debug output if test fails
    if response.status_code != 200:
        print("Response status:", response.status_code)
        print("Response data:", response.data.decode('utf-8'))
    
    assert response.status_code == 200, f"Expected 200 OK but got {response.status_code}. Response: {response.data.decode('utf-8')}"
    assert FlashMessages.CREATE_USER_SUCCESS.value.encode() in response.data, \
        f"Expected success message but got: {response.data.decode('utf-8')}"
    
    # Verify audit log
    log = AuditLog.query.filter_by(
        object_type='User',
        action='create_user'
    ).order_by(AuditLog.id.desc()).first()
    assert log is not None, "No audit log entry found for user creation"
        
    # Debug: Print current user and logged user
    print(f"Admin user ID: {admin_user.id}")
    print(f"Logged user ID: {log.user_id}")
        
    # Verify the audit log user matches the admin user
    assert log.user_id == admin_user.id, \
        f"Expected audit log user ID {admin_user.id} but got {log.user_id}"
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

def test_user_crud_operations(logged_in_admin, db_session, test_user):
    """Test full CRUD operations for users with audit logging"""
    # Create unique test data
    unique_id = str(uuid.uuid4())[:8]
    user_data = {
        'username': f'testuser_{unique_id}',
        'email': f'testuser_{unique_id}@example.com',
        'password': 'TestPass123!',
        'is_admin': False
    }
    
    # Get CSRF token
    create_response = logged_in_admin.get('/admin/users/create')
    csrf_token = extract_csrf_token(create_response.data)
    assert csrf_token is not None
    
    # Create user
    create_response = logged_in_admin.post('/admin/users/create', 
                                         data={
                                             **user_data,
                                             'csrf_token': csrf_token
                                         },
                                         follow_redirects=True)
    assert create_response.status_code == 200
    assert FlashMessages.CREATE_USER_SUCCESS.value.encode() in create_response.data
    
    # Verify user creation
    created_user = User.query.filter_by(username=user_data['username']).first()
    assert created_user is not None
    
    # Verify audit log
    create_log = AuditLog.query.filter_by(
        action='create_user',
        object_type='User',
        object_id=created_user.id
    ).first()
    assert create_log is not None
    assert create_log.ip_address is not None
    
    # Update user
    update_response = logged_in_admin.post(f'/admin/users/{created_user.id}/edit',
                                         data={
                                             'username': f'updated_{unique_id}',
                                             'email': user_data['email'],
                                             'csrf_token': csrf_token
                                         },
                                         follow_redirects=True)
    assert update_response.status_code == 200
    assert FlashMessages.UPDATE_USER_SUCCESS.value.encode() in update_response.data
    
    # Verify update
    updated_user = User.query.get(created_user.id)
    assert updated_user.username == f'updated_{unique_id}'
    
    # Delete user
    delete_response = logged_in_admin.post(f'/admin/users/{created_user.id}/delete',
                                         data={'csrf_token': csrf_token},
                                         follow_redirects=True)
    assert delete_response.status_code == 200
    assert FlashMessages.DELETE_USER_SUCCESS.value.encode() in delete_response.data
    
    # Verify deletion
    deleted_user = User.query.get(created_user.id)
    assert deleted_user is None
    
    # Verify audit logs
    logs = AuditLog.query.filter_by(object_type='User', object_id=created_user.id).all()
    assert len(logs) == 3  # Create, Update, Delete
    
    # Verify all logs have IP addresses
    for log in logs:
        assert log.ip_address is not None
    
    # Use a unique username for the test
    unique_user_data = user_data.copy()
    unique_user_data['username'] = 'unique_testuser'
    
    # Log in the admin user
    with logged_in_admin:
        # First verify if we're already logged in
        with logged_in_admin.session_transaction() as session:
            is_logged_in = '_user_id' in session
                
        if is_logged_in:
            # If already logged in, get CSRF token from a protected page
            dashboard_response = logged_in_admin.get('/admin/dashboard/')
            if dashboard_response.status_code == 308:
                # Follow the redirect if needed
                dashboard_response = logged_in_admin.get(dashboard_response.headers['Location'])
            assert dashboard_response.status_code == 200, \
                f"Dashboard failed with status {dashboard_response.status_code}"
            csrf_token = extract_csrf_token(dashboard_response.data)
        else:
            # If not logged in, get CSRF token from login page
            login_get_response = logged_in_admin.get('/login')
            assert login_get_response.status_code == 200, \
                f"Login page failed with status {login_get_response.status_code}"
            csrf_token = extract_csrf_token(login_get_response.data)
            
        assert csrf_token is not None, \
            "CSRF token not found in response. If already logged in, ensure the dashboard template includes a CSRF token"
        
            
        # Refresh the test_user instance to ensure it's attached to the session
        db_session.refresh(test_user)

        # Perform login with CSRF token
        login_response = logged_in_admin.post('/login', data={
            'username': test_user.username,
            'password': 'AdminPass123!',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        
        assert login_response.status_code == 200, \
            f"Login failed with status {login_response.status_code}. Response: {login_response.data.decode('utf-8')}"
        
        # Refresh test_user within session
        test_user = db_session.merge(test_user)

        # Verify admin user is logged in
        with logged_in_admin.session_transaction() as session:
            assert '_user_id' in session, "Admin user is not logged in"
            logged_in_user = db_session.get(User, session['_user_id'])
            assert logged_in_user.id == test_user.id, \
                f"Logged in user ID {logged_in_user.id} does not match test user ID {test_user.id}"
    
        # Verify CRUD operations
        verify_user_crud_operations(logged_in_admin, test_user, unique_user_data)
    """Test full CRUD operations for users"""
    # Ensure the test user doesn't already exist
    existing_user = User.query.filter_by(username=user_data['username']).first()
    if existing_user:
        db_session.delete(existing_user)
        db_session.commit()
    
    # Use a unique username for the test
    unique_user_data = user_data.copy()
    unique_user_data['username'] = 'unique_testuser'
    
    # Log in the admin user
    with logged_in_admin:
        # First get the CSRF token from the login page
        login_get_response = logged_in_admin.get('/login')
        csrf_token = extract_csrf_token(login_get_response.data)
        assert csrf_token is not None, "CSRF token not found in login page"
            
        # Perform login with CSRF token
        login_response = logged_in_admin.post('/login', data={
            'username': test_user.username,  # Use the test_user's actual username
            'password': 'AdminPass123!',
            'csrf_token': csrf_token
        }, follow_redirects=True)
            
        assert login_response.status_code == 200, \
            f"Login failed with status {login_response.status_code}. Response: {login_response.data.decode('utf-8')}"
            
        # Verify admin user is logged in
        with logged_in_admin.session_transaction() as session:
            assert '_user_id' in session, "Admin user is not logged in"
            assert session['_user_id'] == str(test_user.id), \
                f"Expected logged in user ID {test_user.id} but got {session['_user_id']}"
    
        verify_user_crud_operations(logged_in_admin, test_user, unique_user_data)

def test_get_all_users_sorting(db_session):
    """Test sorting functionality in get_all_users()"""
    # Create test users with password hashes
    user1 = User(
        username='user1',
        email='user1@example.com',
        created_at=datetime(2024, 1, 1, tzinfo=UTC),
        password_hash='hash1'
    )
    user2 = User(
        username='user2',
        email='user2@example.com',
        created_at=datetime(2024, 1, 2, tzinfo=UTC),
        password_hash='hash2'
    )
    user3 = User(
        username='user3',
        email='user3@example.com',
        created_at=datetime(2024, 1, 3, tzinfo=UTC),
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

def test_create_user(logged_in_admin):
    """Test user creation"""
    # Get CSRF token
    create_response = logged_in_admin.get('/admin/users/create')
    csrf_token = extract_csrf_token(create_response.data)
    
    # Create user
    response = logged_in_admin.post('/admin/users/create', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'StrongPass123!',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'User created successfully' in response.data
    
    # Verify user exists
    user = User.query.filter_by(username='testuser').first()
    assert user is not None
    assert user.email == 'test@example.com'
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
    decoded_data = response_data.decode('utf-8')
    
    # Look for CSRF token in hidden input with id="csrf_token"
    csrf_input = re.search(r'<input[^>]*id="csrf_token"[^>]*value="(.+?)"', decoded_data)
    if csrf_input:
        return csrf_input.group(1)
    
    # Look for CSRF token in meta tag as fallback
    meta_token = re.search(r'<meta[^>]*name="csrf-token"[^>]*content="(.+?)"', decoded_data)
    if meta_token:
        return meta_token.group(1)
    
    # Look for CSRF token in any hidden input as last resort
    hidden_input = re.search(r'<input[^>]*type="hidden"[^>]*name="csrf_token"[^>]*value="(.+?)"', decoded_data)
    if hidden_input:
        return hidden_input.group(1)
    
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
