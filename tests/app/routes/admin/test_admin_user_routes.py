import pytest
import logging
import re
from datetime import datetime, timezone, timedelta
from flask import url_for
from app.services.user_service import get_all_users
from flask_login import current_user
from app.models.user import User
from app.models.audit_log import AuditLog
from app.models.notification import Notification
from tests.conftest import logged_in_admin, db_session
from app.constants import FlashMessages, FlashCategory
from werkzeug.security import generate_password_hash, check_password_hash
from tests.utils import assert_flash_message, create_user_data, extract_csrf_token
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
    """Provides a test client with proper session and context management."""
    with app.app_context():
        # Initialize rate limiter if present
        if 'limiter' in app.extensions:
            limiter = app.extensions['limiter']
            limiter.enabled = False
            
            # Initialize storage if needed
            if not hasattr(limiter, '_storage') or limiter._storage is None:
                limiter.init_app(app)
            
            # Reset limiter if storage is available
            if hasattr(limiter, '_storage') and limiter._storage is not None:
                try:
                    limiter.reset()
                except Exception as e:
                    app.logger.warning(f"Failed to reset rate limiter: {str(e)}")
        
        # Create test client within application context
        client = app.test_client()
        
        # Push request context
        with app.test_request_context():
            with client.session_transaction() as session:
                session['csrf_token'] = 'test-csrf-token'
            yield client
            
        # Ensure proper cleanup
        try:
            User.query.filter(User.username.like('testuser_%')).delete()
            AuditLog.query.filter(AuditLog.user_id.isnot(None)).delete()
            Notification.query.delete()
            db.session.commit()
            db.session.remove()
        except:
            pass

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
+    response = test_client.post('/admin/users/create', 
+                              data=test_data,
+                              follow_redirects=True)
+    
+    # Debug output if test fails
+    if response.status_code != 200:
+        print("Response status:", response.status_code)
+        print("Response data:", response.data.decode('utf-8'))
+    
+    assert response.status_code == 200, f"Expected 200 OK but got {response.status_code}. Response: {response.data.decode('utf-8')}"
+    assert_flash_message(response, FlashMessages.CREATE_USER_SUCCESS)
+    
+    # Verify audit log
+    log = AuditLog.query.filter_by(
+        object_type='User',
+        action='create_user'
+    ).order_by(AuditLog.id.desc()).first()
+    assert log is not None, "No audit log entry found for user creation"
+        
+    # Debug: Print current user and logged user
+    print(f"Admin user ID: {admin_user.id}")
+    print(f"Logged user ID: {log.user_id}")
+        
+    # Verify the audit log user matches the admin user
+    assert log.user_id == admin_user.id, \
+        f"Expected audit log user ID {admin_user.id} but got {log.user_id}"
+    assert log.ip_address is not None
+    
+    # Read 
+    response = test_client.get('/admin/users')
+    assert response.status_code == 200
+    assert test_data['username'].encode() in response.data
+    
+    # Update
+    updated_data = test_data.copy()
+    updated_data['username'] = 'updateduser'
+    response = test_client.post('/admin/users/1/edit',
+                              data=updated_data,
+                              follow_redirects=True)
+    assert response.status_code == 200
+    assert_flash_message(response, FlashMessages.UPDATE_USER_SUCCESS)
+    
+    # Verify audit log
+    log = AuditLog.query.filter_by(
+        object_type='User',
+        action='update_user'
+    ).first()
+    assert log is not None
+    
+    # Delete
+    response = test_client.post('/admin/users/1/delete',
+                              follow_redirects=True)
+    assert response.status_code == 200
+    assert_flash_message(response, FlashMessages.DELETE_USER_SUCCESS)
+    
+    # Verify audit log
+    log = AuditLog.query.filter_by(
+        object_type='User',
+        action='delete_user'
+    ).first()
+    assert log is not None
+    assert_flash_message(response, FlashMessages.CREATE_USER_SUCCESS)
+    
+    # Verify audit log
+    log = AuditLog.query.filter_by(
+        object_type='User',
+        action='create_user'
+    ).first()
+    assert log is not None
+    assert log.user_id == admin_user.id
+    assert log.ip_address is not None
+    
+    # Read 
+    response = test_client.get('/admin/users')
+    assert response.status_code == 200
+    assert test_data['username'].encode() in response.data
+    
+    # Update
+    updated_data = test_data.copy()
+    updated_data['username'] = 'updateduser'
+    response = test_client.post('/admin/users/1/edit',
+                              data=updated_data,
+                              follow_redirects=True)
+    assert response.status_code == 200
+    assert_flash_message(response, FlashMessages.UPDATE_USER_SUCCESS)
+    
+    # Verify audit log
+    log = AuditLog.query.filter_by(
+        object_type='User',
+        action='update_user'
+    ).first()
+    assert log is not None
+    
+    # Delete
+    response = test_client.post('/admin/users/1/delete',
+                              follow_redirects=True)
+    assert response.status_code == 200
+    assert_flash_message(response, FlashMessages.DELETE_USER_SUCCESS)
+    
+    # Verify audit log
+    log = AuditLog.query.filter_by(
+        object_type='User',
+        action='delete_user'
+    ).first()
+    assert log is not None
+    
+from flask import current_app
+from unittest.mock import patch, MagicMock
+ 
+ 
+def test_user_crud_operations(logged_in_admin, db_session, test_user, app):
+    """Test full CRUD operations with enhanced error handling"""
+    logger = logging.getLogger(__name__)
+    logger.info("Starting user CRUD operations test")
+    
+    # Test audit log creation
+    with app.app_context():
+        try:
+            # Test valid audit log
+            audit_log = AuditLog.create(
+                user_id=test_user.id,
+                action="test_action",
+                commit=True
+            )
+            assert audit_log is not None
+            
+            # Test invalid audit log
+            with pytest.raises(ValueError) as exc_info:
+                AuditLog.create(
+                    user_id=test_user.id,
+                    action=None,  # Invalid
+                    commit=True
+                )
+            assert "Action is required" in str(exc_info.value)
+             
+            # Verify no invalid log was created
+            invalid_logs = AuditLog.query.filter_by(user_id=test_user.id, action=None).all()
+            assert len(invalid_logs) == 0
+             
+        except Exception as e:
+            logger.error(f"Test failed with error: {str(e)}")
+            raise
+ 
+    # Test audit log rollback
+    with app.app_context():
+        try:
+            # Test valid audit log creation
+            AuditLog.create(
+                user_id=test_user.id,
+                action="test_action",  # Valid action
+                commit=True
+            )
+            # Verify audit log was created
+            log = AuditLog.query.filter_by(user_id=test_user.id).first()
+            assert log is not None
+            assert log.action == "test_action"
+        except Exception as e:
+            logger.error(f"Error testing audit log rollback: {str(e)}")
+            raise
+         
+        # Test invalid audit log creation
+        with pytest.raises(ValueError) as exc_info:
+            AuditLog.create(
+                user_id=test_user.id,
+                action=None,  # Invalid - should raise error
+                commit=True
+            )
+        assert str(exc_info.value) == "Action is required"
+             
+        # Verify no invalid log was created
+        invalid_logs = AuditLog.query.filter_by(user_id=test_user.id, action=None).all()
+        assert len(invalid_logs) == 0
+ 
+        # Test notification error handling
+        notification = Notification(
+            message="Test notification",
+            type="USER_ACTION",
+            user_id=test_user.id
+        )
+        db_session.add(notification)
+        db_session.commit()
+ 
+        # Force an error by marking invalid notification as read
+        invalid_notification = Notification()
+        with pytest.raises(ValueError) as exc_info:
+            invalid_notification.mark_as_read()
+        assert str(exc_info.value) == "Cannot mark unsaved notification as read"
+ 
+    # Set up session
+    with logged_in_admin.session_transaction() as session:
+        session['_user_id'] = str(test_user.id)
+        session['_fresh'] = True
+        session['csrf_token'] = 'test-csrf-token'
+ 
+    # Get create form and extract CSRF token
+    create_response = logged_in_admin.get('/admin/users/create')
+    assert create_response.status_code == 200
+    csrf_token = extract_csrf_token(create_response.data)
+    if csrf_token is None:
+        logging.error("CSRF token not found in response. Response content:\n%s", 
+                    create_response.data.decode('utf-8')[:1000])
+    assert csrf_token is not None, "CSRF token not found in create form response"
+ 
+    """Test full CRUD operations with audit logging and notifications"""
+     
+    # Create unique test data
+    unique_id = str(uuid.uuid4())[:8]
+    user_data = {
+        'username': f'testuser_{unique_id}',
+        'email': f'testuser_{unique_id}@example.com',
+        'password': 'TestPass123!',
+        'is_admin': False
+    }
+ 
+    # Perform all operations within the logged_in_admin context
+    with logged_in_admin.application.test_request_context():
+        # Set up session and CSRF token
+        with logged_in_admin.session_transaction() as session:
+            session['_user_id'] = str(test_user.id)
+            session['_fresh'] = True
+            session['csrf_token'] = 'test-csrf-token'
+         
+        # Get create form and extract CSRF token
+        create_response = logged_in_admin.get('/admin/users/create')
+        assert create_response.status_code == 200
+         
+        # Extract CSRF token with debug logging
+        csrf_token = extract_csrf_token(create_response.data)
+        if csrf_token is None:
+            logging.error("CSRF token not found in response. Response content:\n%s", 
+                        create_response.data.decode('utf-8')[:1000])
+        assert csrf_token is not None, "CSRF token not found in create form response"
+ 
+        # Create user
+        response = logged_in_admin.post('/admin/users/create', data={
+            'username': user_data['username'],
+            'email': user_data['email'],
+            'password': user_data['password'],
+            'is_admin': user_data['is_admin'],
+            'csrf_token': csrf_token
+        }, follow_redirects=True)
+ 
+        assert response.status_code == 200
+        assert_flash_message(response, FlashMessages.CREATE_USER_SUCCESS)
+ 
+        # Verify user creation
+        created_user = User.query.filter_by(username=user_data['username']).first()
+        assert created_user is not None
+             
+        # Verify audit log
+        audit_log = AuditLog.query.filter_by(
+            action='POST',
+            object_type='User',
+            object_id=created_user.id
+        ).first()
+        assert audit_log is not None
+        assert audit_log.user_id == test_user.id
+        assert audit_log.ip_address is not None
+        assert audit_log.endpoint == 'admin.user.create'
+             
+        # Verify notification
+        notification = Notification.query.filter_by(
+            type='user_created',
+            related_object_id=created_user.id
+        ).first()
+        assert notification is not None
+        assert notification.message == f'User {user_data["username"]} was created'
+        csrf_token = extract_csrf_token(create_response.data)
+        assert csrf_token is not None
+ 
+        # Create user
+        # Create form data with proper field names
+        form_data = {
+            'username': user_data['username'],
+            'email': user_data['email'],
+            'password': 'StrongPass123!',  # Valid password
+            'is_admin': 'False',  # Must be string for form submission
+            'csrf_token': csrf_token
+        }
+             
+        # Submit the form with proper headers
+        create_response = logged_in_admin.post('/admin/users/create',
+                                             data=form_data,
+                                             follow_redirects=True,
+                                             headers={
+                                                 'X-CSRFToken': csrf_token,
+                                                 'Content-Type': 'application/x-www-form-urlencoded'
+                                             })
+             
+        # Verify user creation
+        assert create_response.status_code == 200, \
+            f"Expected 200 OK but got {create_response.status_code}. Response: {create_response.data.decode('utf-8')}"
+        assert_flash_message(create_response, FlashMessages.CREATE_USER_SUCCESS)
+             
+        # Verify user exists in database
+        created_user = User.query.filter_by(username=user_data['username']).first()
+        assert created_user is not None, "User was not created in database"
+        assert hasattr(created_user, 'id'), "Created user does not have an id attribute"
+        assert created_user.email == user_data['email'], \
+            f"Expected email {user_data['email']} but got {created_user.email}"
+        assert created_user.password_hash is not None, "Password hash was not set"
+        assert created_user.is_admin == user_data['is_admin'], \
+            f"Expected is_admin {user_data['is_admin']} but got {created_user.is_admin}"
+             
+        # Verify audit log
+        audit_log = AuditLog.query.filter_by(
+            action=FlashMessages.AUDIT_CREATE.value,
+            object_type='User',
+            object_id=created_user.id
+        ).first()
+        assert audit_log is not None, "No audit log entry found for user creation"
+        assert audit_log.user_id == test_user.id, \
+            f"Expected audit log user ID {test_user.id} but got {audit_log.user_id}"
+        assert audit_log.ip_address is not None, "Audit log missing IP address"
+        assert audit_log.details_before is None, "Expected no before state for new user"
+        assert audit_log.details_after == {
+            'username': user_data['username'],
+            'email': user_data['email'],
+            'is_admin': user_data['is_admin']
+        }, "Audit log after state does not match created user"
+             
+        # Verify notification
+        notification = Notification.query.filter_by(
+            type='user_created',
+            message=f'User {user_data["username"]} was created'
+        ).first()
+        assert notification is not None, "No notification created for user creation"
+        assert notification.read_status is False, "Notification should be unread"
+    assert create_response.status_code == 200
+    assert_flash_message(create_response, FlashMessages.CREATE_USER_SUCCESS)
+     
+    # Verify user creation
+    created_user = User.query.filter_by(username=user_data['username']).first()
+    assert created_user is not None
+     
+    # Verify audit log
+    create_log = AuditLog.query.filter_by(
+        action='create_user',
+        object_type='User',
+        object_id=created_user.id
+    ).first()
+    assert create_log is not None
+    assert create_log.ip_address is not None
+         
+    # Verify notification was created
+    notification = Notification.query.filter_by(
+        type='user_created',
+        message=f'User {user_data["username"]} was created'
+    ).first()
+    assert notification is not None
+    assert notification.read_status is False
+     
+    # Update user
+    update_response = logged_in_admin.post(f'/admin/users/{created_user.id}/edit',
+                                          data={
+                                              'username': f'updated_{unique_id}',
+                                              'email': user_data['email'],
+                                              'csrf_token': csrf_token
+                                          },
+                                          follow_redirects=True)
+    assert update_response.status_code == 200
+    assert_flash_message(update_response, FlashMessages.UPDATE_USER_SUCCESS)
+     
+    # Verify update
+    updated_user = User.query.get(created_user.id)
+    assert updated_user.username == f'updated_{unique_id}'
+     
+    # Delete user
+    delete_response = logged_in_admin.post(f'/admin/users/{created_user.id}/delete',
+                                          data={'csrf_token': csrf_token},
+                                          follow_redirects=True)
+    assert delete_response.status_code == 200
+    assert_flash_message(delete_response, FlashMessages.DELETE_USER_SUCCESS)
+     
+    # Verify deletion
+    deleted_user = User.query.get(created_user.id)
+    assert deleted_user is None
+     
+    # Verify audit logs
+    logs = AuditLog.query.filter_by(object_type='User', object_id=created_user.id).all()
+    assert len(logs) == 3, f"Expected 3 audit logs, got {len(logs)}"
+         
+    # Verify create log
+    create_log = next(log for log in logs if log.action == 'create_user')
+    assert create_log is not None
+    assert create_log.details == f"Created user {user_data['username']}"
+         
+    # Verify update log
+    update_log = next(log for log in logs if log.action == 'update_user')
+    assert update_log is not None
+    assert update_log.details == f"Updated username from {user_data['username']} to updated_{unique_id}"
+         
+    # Verify delete log
+    delete_log = next(log for log in logs if log.action == 'delete_user')
+    assert delete_log is not None
+    assert delete_log.details == f"Deleted user {user_data['username']}"
+    assert delete_log.ip_address is not None
+         
+    # Verify notification was created
+    notification = Notification.query.filter_by(
+        type='user_deleted',
+        message=f'User {user_data["username"]} was deleted'
+    ).first()
+    assert notification is not None
+    assert notification.read_status is False
+     
+    # Verify all logs have IP addresses
+    for log in logs:
+        assert log.ip_address is not None
+     
+    # Use a unique username for the test
+    unique_user_data = user_data.copy()
+    unique_user_data['username'] = 'unique_testuser'
+     
+    # Log in the admin user
+    with logged_in_admin:
+        # First verify if we're already logged in
+        with logged_in_admin.session_transaction() as session:
+            is_logged_in = '_user_id' in session
+                 
+        if is_logged_in:
+            # If already logged in, get CSRF token from a protected page
+            dashboard_response = logged_in_admin.get('/admin/dashboard/')
+            if dashboard_response.status_code == 308:
+                # Follow the redirect if needed
+                dashboard_response = logged_in_admin.get(dashboard_response.headers['Location'])
+            assert dashboard_response.status_code == 200, \
+                f"Dashboard failed with status {dashboard_response.status_code}"
+            csrf_token = extract_csrf_token(dashboard_response.data)
+        else:
+            # If not logged in, get CSRF token from login page
+            login_get_response = logged_in_admin.get('/login')
+            assert login_get_response.status_code == 200, \
+                f"Login page failed with status {login_get_response.status_code}"
+            csrf_token = extract_csrf_token(login_get_response.data)
+             
+        assert csrf_token is not None, \
+            "CSRF token not found in response. If already logged in, ensure the dashboard template includes a CSRF token"
+         
+             
+        # Ensure the test_user is attached to the session
+        test_user = db_session.merge(test_user)
+ 
+        # Perform login with CSRF token
+        with logged_in_admin.session_transaction() as session:
+            session['csrf_token'] = csrf_token
+            session['_fresh'] = True  # Mark session as fresh
+            session['_user_id'] = str(test_user.id)  # Set user ID directly
+            session['_id'] = 'test-session-id'
+             
+        # Verify session is properly set
+        with logged_in_admin.session_transaction() as session:
+            assert '_user_id' in session
+            assert session['_user_id'] == str(test_user.id)
+         
+        # Perform login with CSRF token to get a response
+        login_response = logged_in_admin.post('/login', data={
+            'username': test_user.username,
+            'password': 'AdminPass123!',
+            'csrf_token': csrf_token
+        }, follow_redirects=True)
+         
+        assert login_response.status_code == 200, \
+            f"Login failed with status {login_response.status_code}. Response: {login_response.data.decode('utf-8')}"
+         
+        # Refresh test_user within session
+        test_user = db_session.merge(test_user)
+ 
+        # Verify admin user is logged in
+        with logged_in_admin.session_transaction() as session:
+            assert '_user_id' in session, "Admin user is not logged in"
+            logged_in_user = db_session.get(User, session['_user_id'])
+            assert logged_in_user.id == test_user.id, \
+                f"Logged in user ID {logged_in_user.id} does not match test user ID {test_user.id}"
+     
+        # Verify CRUD operations
+        verify_user_crud_operations(logged_in_admin, test_user, unique_user_data)
+    """Test full CRUD operations for users"""
+    # Ensure the test user doesn't already exist
+    existing_user = User.query.filter_by(username=user_data['username']).first()
+    if existing_user:
+        db_session.delete(existing_user)
+        db_session.commit()
+    
+    # Use a unique username for the test
+    unique_user_data = user_data.copy()
+    unique_user_data['username'] = 'unique_testuser'
+    
+    # Log in the admin user
+    with logged_in_admin:
+        # First get the CSRF token from the login page
+        login_get_response = logged_in_admin.get('/login')
+        csrf_token = extract_csrf_token(login_get_response.data)
+        assert csrf_token is not None, "CSRF token not found in login page"
+            
+        # Perform login with CSRF token
+        login_response = logged_in_admin.post('/login', data={
+            'username': test_user.username,  # Use the test_user's actual username
+            'password': 'AdminPass123!',
+            'csrf_token': csrf_token
+        }, follow_redirects=True)
+            
+        assert login_response.status_code == 200, \
+            f"Login failed with status {login_response.status_code}. Response: {login_response.data.decode('utf-8')}"
+            
+        # Verify admin user is logged in
+        with logged_in_admin.session_transaction() as session:
+            assert '_user_id' in session, "Admin user is not logged in"
+            assert session['_user_id'] == str(test_user.id), \
+                f"Expected logged in user ID {test_user.id} but got {session['_user_id']}"
+    
+        verify_user_crud_operations(logged_in_admin, test_user, unique_user_data)
+ 
+def test_get_all_users_sorting(db_session):
+    """Test sorting functionality in get_all_users()"""
+    # Create test users with password hashes
+    user1 = User(
+        username='user1',
+        email='user1@example.com',
+        created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
+        password_hash='hash1'
+    )
+    user2 = User(
+        username='user2',
+        email='user2@example.com',
+        created_at=datetime(2024, 1, 2, tzinfo=timezone.utc),
+        password_hash='hash2'
+    )
+    user3 = User(
+        username='user3',
+        email='user3@example.com',
+        created_at=datetime(2024, 1, 3, tzinfo=timezone.utc),
+        password_hash='hash3'
+    )
+    db_session.add_all([user1, user2, user3])
+    db_session.commit()
+ 
+    # Test username ascending
+    result = get_all_users(sort_by='username', sort_order='asc')
+    assert [u.username for u in result.items] == ['user1', 'user2', 'user3']
+ 
+    # Test username descending
+    result = get_all_users(sort_by='username', sort_order='desc')
+    assert [u.username for u in result.items] == ['user3', 'user2', 'user1']
+ 
+    # Test email ascending
+    result = get_all_users(sort_by='email', sort_order='asc')
+    assert [u.email for u in result.items] == ['user1@example.com', 'user2@example.com', 'user3@example.com']
+ 
+    # Test created_at descending (default)
+    result = get_all_users()
+    assert [u.username for u in result.items] == ['user3', 'user2', 'user1']
+ 
+def test_create_user(logged_in_admin, db_session):
+    """Test user creation"""
+    # Get CSRF token
+    create_response = logged_in_admin.get('/admin/users/create')
+    csrf_token = extract_csrf_token(create_response.data)
+     
+    # Test valid user creation
+    response = logged_in_admin.post('/admin/users/create', data={
+        'username': 'testuser',
+        'email': 'test@example.com',
+        'password': 'StrongPass123!',
+        'csrf_token': csrf_token
+    }, follow_redirects=True)
+     
+    assert response.status_code == 200
+    assert_flash_message(response, FlashMessages.CREATE_USER_SUCCESS)
+     
+    # Verify user exists
+    user = User.query.filter_by(username='testuser').first()
+    assert user is not None
+    assert user.email == 'test@example.com'
+     
+    # Test duplicate username
+    response = logged_in_admin.post('/admin/users/create', data={
+        'username': 'testuser',  # Duplicate username
+        'email': 'test2@example.com',
+        'password': 'StrongPass123!',
+        'csrf_token': csrf_token
+    }, follow_redirects=True)
+     
+    assert response.status_code == 200
+    assert_flash_message(response, FlashMessages.CREATE_USER_DUPLICATE)
+     
+    # Test invalid email
+    response = logged_in_admin.post('/admin/users/create', data={
+        'username': 'testuser2',
+        'email': 'invalid-email',
+        'password': 'StrongPass123!',
+        'csrf_token': csrf_token
+     },