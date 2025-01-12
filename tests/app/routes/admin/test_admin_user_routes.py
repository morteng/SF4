import pytest
import logging
import re
import uuid
from datetime import datetime, timezone, timedelta
from flask import url_for, current_app
from flask_login import current_user
from werkzeug.security import generate_password_hash, check_password_hash
from unittest.mock import patch, MagicMock

from app.services.user_service import get_all_users
from app.models.user import User
from app.models.audit_log import AuditLog
from app.models.notification import Notification
from app.constants import FlashMessages, FlashCategory
from app.utils import validate_password_strength
from app import db

from tests.conftest import logged_in_admin, db_session
from tests.utils import assert_flash_message, create_user_data, extract_csrf_token


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

        client = app.test_client()

        with app.test_request_context():
            with client.session_transaction() as session:
                session['csrf_token'] = 'test-csrf-token'
            yield client

        # Cleanup
        try:
            User.query.filter(User.username.like('testuser_%')).delete()
            AuditLog.query.filter(AuditLog.user_id.isnot(None)).delete()
            Notification.query.delete()
            db.session.commit()
            db.session.remove()
        except:
            pass


@pytest.fixture(scope='function')
def test_user(db_session):
    """Provide a test admin user with unique credentials."""
    db_session.query(User).filter(User.username.like('test_admin_%')).delete()

    user = User(
        username=f'test_admin_{uuid.uuid4().hex[:8]}',
        email=f'test_admin_{uuid.uuid4().hex[:8]}@example.com',
        password_hash=generate_password_hash('AdminPass123!'),
        is_admin=True
    )
    db_session.add(user)
    db_session.commit()
    yield user

    user = db_session.merge(user)
    db_session.delete(user)
    db_session.commit()


def verify_user_crud_operations(test_client, admin_user, test_data):
    """
    Verify full CRUD operations for users
    in a single pass to avoid repeated code.
    """
    # 1) Get the CSRF token for creating a user
    create_response = test_client.get('/admin/users/create')
    assert create_response.status_code == 200
    csrf_token = extract_csrf_token(create_response.data)
    assert csrf_token is not None

    # 2) Create user
    test_data['csrf_token'] = csrf_token
    response = test_client.post('/admin/users/create', data=test_data, follow_redirects=True)
    if response.status_code != 200:
        print("Response status:", response.status_code)
        print("Response data:", response.data.decode('utf-8'))

    assert response.status_code == 200, f"Expected 200 but got {response.status_code}"
    assert_flash_message(response, FlashMessages.CREATE_USER_SUCCESS)

    # Verify create audit log
    log = AuditLog.query.filter_by(
        object_type='User',
        action='create_user'
    ).order_by(AuditLog.id.desc()).first()
    assert log is not None, "No audit log entry found for user creation"
    assert log.user_id == admin_user.id, \
        f"Expected audit log user ID {admin_user.id} but got {log.user_id}"
    assert log.ip_address is not None

    # 3) Read users
    response = test_client.get('/admin/users')
    assert response.status_code == 200
    assert test_data['username'].encode() in response.data

    # 4) Update user
    updated_data = test_data.copy()
    updated_data['username'] = 'updateduser'
    response = test_client.post('/admin/users/1/edit',
                                data=updated_data,
                                follow_redirects=True)
    assert response.status_code == 200
    assert_flash_message(response, FlashMessages.UPDATE_USER_SUCCESS)

    # Verify update log
    log = AuditLog.query.filter_by(
        object_type='User',
        action='update_user'
    ).first()
    assert log is not None

    # 5) Delete user
    response = test_client.post('/admin/users/1/delete',
                                follow_redirects=True)
    assert response.status_code == 200
    assert_flash_message(response, FlashMessages.DELETE_USER_SUCCESS)

    # Verify delete audit log
    log = AuditLog.query.filter_by(
        object_type='User',
        action='delete_user'
    ).first()
    assert log is not None


def test_user_crud_operations(logged_in_admin, db_session, test_user, app):
    """Test full CRUD operations with audit logs and notifications."""
    logger = logging.getLogger(__name__)
    logger.info("Starting user CRUD operations test")

    # Test some audit log creation scenarios
    with app.app_context():
        # Valid log
        audit_log = AuditLog.create(user_id=test_user.id, action="test_action", commit=True)
        assert audit_log is not None

        # Invalid log
        with pytest.raises(ValueError) as exc_info:
            AuditLog.create(user_id=test_user.id, action=None, commit=True)
        assert "Action is required" in str(exc_info.value)

        # Ensure no invalid logs got saved
        invalid_logs = AuditLog.query.filter_by(user_id=test_user.id, action=None).all()
        assert len(invalid_logs) == 0

    # Test rollback approach
    with app.app_context():
        # Valid log
        AuditLog.create(user_id=test_user.id, action="test_action", commit=True)
        log = AuditLog.query.filter_by(user_id=test_user.id).first()
        assert log is not None and log.action == "test_action"

        # Invalid log again
        with pytest.raises(ValueError) as exc_info:
            AuditLog.create(user_id=test_user.id, action=None, commit=True)
        assert str(exc_info.value) == "Action is required"

        invalid_logs = AuditLog.query.filter_by(user_id=test_user.id, action=None).all()
        assert len(invalid_logs) == 0

        # Test notification error handling
        notification = Notification(
            message="Test notification",
            type="USER_ACTION",
            user_id=test_user.id
        )
        db_session.add(notification)
        db_session.commit()

        # Attempt to mark an unsaved notification
        invalid_notification = Notification()
        with pytest.raises(ValueError) as exc_info:
            invalid_notification.mark_as_read()
        assert str(exc_info.value) == "Cannot mark unsaved notification as read"

    # Set up session for the admin user
    with logged_in_admin.session_transaction() as session:
        session['_user_id'] = str(test_user.id)
        session['_fresh'] = True
        session['csrf_token'] = 'test-csrf-token'

    # Get create form and fetch CSRF
    create_response = logged_in_admin.get('/admin/users/create')
    assert create_response.status_code == 200
    csrf_token = extract_csrf_token(create_response.data)
    assert csrf_token is not None, "CSRF token not found in create form response"

    # We’ll do the actual user CRUD test with a unique username
    unique_id = str(uuid.uuid4())[:8]
    user_data_dict = {
        'username': f'testuser_{unique_id}',
        'email': f'testuser_{unique_id}@example.com',
        'password': 'TestPass123!',
        'is_admin': False
    }

    with logged_in_admin.application.test_request_context():
        with logged_in_admin.session_transaction() as session:
            session['_user_id'] = str(test_user.id)
            session['_fresh'] = True
            session['csrf_token'] = 'test-csrf-token'

        create_response = logged_in_admin.get('/admin/users/create')
        csrf_token = extract_csrf_token(create_response.data)
        assert csrf_token is not None

        # Create user
        response = logged_in_admin.post('/admin/users/create', data={
            'username': user_data_dict['username'],
            'email': user_data_dict['email'],
            'password': user_data_dict['password'],
            'is_admin': user_data_dict['is_admin'],
            'csrf_token': csrf_token
        }, follow_redirects=True)

        assert response.status_code == 200
        assert_flash_message(response, FlashMessages.CREATE_USER_SUCCESS)

        # Check user creation
        created_user = User.query.filter_by(username=user_data_dict['username']).first()
        assert created_user is not None

        # Check audit log
        audit_log = AuditLog.query.filter_by(
            action='POST',
            object_type='User',
            object_id=created_user.id
        ).first()
        assert audit_log is not None
        assert audit_log.user_id == test_user.id

        # Check notification
        notification = Notification.query.filter_by(
            type='user_created',
            related_object_id=created_user.id
        ).first()
        assert notification is not None
        assert notification.message == f'User {user_data_dict["username"]} was created'

        # Create form data for a second user (for demonstration)
        form_data = {
            'username': user_data_dict['username'],
            'email': user_data_dict['email'],
            'password': 'StrongPass123!',
            'is_admin': 'False',
            'csrf_token': csrf_token
        }
        create_response = logged_in_admin.post('/admin/users/create',
                                               data=form_data,
                                               follow_redirects=True,
                                               headers={
                                                   'X-CSRFToken': csrf_token,
                                                   'Content-Type': 'application/x-www-form-urlencoded'
                                               })
        assert create_response.status_code == 200, \
            f"Expected 200 but got {create_response.status_code}"
        assert_flash_message(create_response, FlashMessages.CREATE_USER_SUCCESS)

        # Check new user data
        created_user = User.query.filter_by(username=user_data_dict['username']).first()
        assert created_user is not None
        assert created_user.email == user_data_dict['email']

        # Verify create audit log
        audit_log = AuditLog.query.filter_by(
            action=FlashMessages.AUDIT_CREATE.value,
            object_type='User',
            object_id=created_user.id
        ).first()
        assert audit_log is not None
        assert audit_log.user_id == test_user.id
        assert audit_log.ip_address is not None

        # Notification
        notification = Notification.query.filter_by(
            type='user_created',
            message=f'User {user_data_dict["username"]} was created'
        ).first()
        assert notification is not None
        assert notification.read_status is False

    # Actually use the verification function to confirm CRUD:
    unique_user_data = user_data_dict.copy()
    unique_user_data['username'] = 'unique_testuser'
    with logged_in_admin:
        # Log in if needed
        with logged_in_admin.session_transaction() as session:
            is_logged_in = '_user_id' in session

        if not is_logged_in:
            # If not logged in, do that
            login_get_response = logged_in_admin.get('/login')
            csrf_token = extract_csrf_token(login_get_response.data)
            login_response = logged_in_admin.post('/login', data={
                'username': test_user.username,
                'password': 'AdminPass123!',
                'csrf_token': csrf_token
            }, follow_redirects=True)
            assert login_response.status_code == 200

        # Double-check that we’re admin
        with logged_in_admin.session_transaction() as session:
            assert '_user_id' in session
            logged_in_user = db_session.get(User, session['_user_id'])
            assert logged_in_user.id == test_user.id

        verify_user_crud_operations(logged_in_admin, test_user, unique_user_data)


def test_get_all_users_sorting(db_session):
    """Test sorting functionality in get_all_users()."""
    user1 = User(
        username='user1',
        email='user1@example.com',
        created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        password_hash='hash1'
    )
    user2 = User(
        username='user2',
        email='user2@example.com',
        created_at=datetime(2024, 1, 2, tzinfo=timezone.utc),
        password_hash='hash2'
    )
    user3 = User(
        username='user3',
        email='user3@example.com',
        created_at=datetime(2024, 1, 3, tzinfo=timezone.utc),
        password_hash='hash3'
    )
    db_session.add_all([user1, user2, user3])
    db_session.commit()

    # Username ascending
    result = get_all_users(sort_by='username', sort_order='asc')
    assert [u.username for u in result.items] == ['user1', 'user2', 'user3']

    # Username descending
    result = get_all_users(sort_by='username', sort_order='desc')
    assert [u.username for u in result.items] == ['user3', 'user2', 'user1']

    # Email ascending
    result = get_all_users(sort_by='email', sort_order='asc')
    assert [u.email for u in result.items] == [
        'user1@example.com',
        'user2@example.com',
        'user3@example.com'
    ]

    # Default sort (created_at desc)
    result = get_all_users()
    assert [u.username for u in result.items] == ['user3', 'user2', 'user1']


def test_create_user(logged_in_admin, db_session, user_data):
    """Test user creation page and logic."""
    create_response = logged_in_admin.get('/admin/users/create')
    csrf_token = extract_csrf_token(create_response.data)

    # Valid user creation
    response = logged_in_admin.post('/admin/users/create', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'StrongPass123!',
        'csrf_token': csrf_token
    }, follow_redirects=True)

    assert response.status_code == 200
    assert_flash_message(response, FlashMessages.CREATE_USER_SUCCESS)

    # Check existence
    user = User.query.filter_by(username='testuser').first()
    assert user is not None
    assert user.email == 'test@example.com'

    # Duplicate
    response = logged_in_admin.post('/admin/users/create', data={
        'username': 'testuser',
        'email': 'test2@example.com',
        'password': 'StrongPass123!',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    assert response.status_code == 200
    assert_flash_message(response, FlashMessages.CREATE_USER_DUPLICATE)

    # Invalid email
    response = logged_in_admin.post('/admin/users/create', data={
        'username': 'testuser2',
        'email': 'invalid-email',
        'password': 'StrongPass123!',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    assert response.status_code == 200
    assert_flash_message(response, FlashMessages.CREATE_USER_INVALID_EMAIL)

    # Weak password
    response = logged_in_admin.post('/admin/users/create', data={
        'username': 'testuser3',
        'email': 'test3@example.com',
        'password': 'weak',
        'csrf_token': csrf_token
    }, follow_redirects=True)
    assert response.status_code == 200
    assert_flash_message(response, FlashMessages.CREATE_USER_WEAK_PASSWORD)

    # Another GET request
    create_response = logged_in_admin.get(url_for('admin.user.create'))
    assert create_response.status_code == 200
    csrf_token = extract_csrf_token(create_response.data)
    assert csrf_token is not None

    # Another user create
    response = logged_in_admin.post(url_for('admin.user.create'), data={
        'username': user_data['username'],
        'email': user_data['email'],
        'password': user_data['password'],
        'is_admin': False,
        'csrf_token': csrf_token
    }, follow_redirects=True)
    assert response.status_code == 200
    assert_flash_message(response, FlashMessages.CREATE_USER_SUCCESS)

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
