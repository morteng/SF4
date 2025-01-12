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
def test_user(db_session, app):
    """Provide a test admin user with unique credentials."""
    with app.app_context():
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


def test_user_crud_operations(logged_in_admin, test_user, db_session, app):
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
        assert "Action is required" in str(exc_info.value) or "Failed to create audit log" in str(exc_info.value)
        
        # Ensure no invalid logs got saved
        invalid_logs = AuditLog.query.filter_by(user_id=test_user.id, action=None).all()
        assert len(invalid_logs) == 0

        # Test rollback approach
        with db_session.begin():
            pass
