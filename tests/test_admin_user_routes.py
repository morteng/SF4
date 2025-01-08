import pytest
from flask import url_for
from app.models.user import User
from app.models.audit_log import AuditLog
from app.models.notification import Notification

def test_admin_create_user_success(logged_in_admin, db_session, client):
    """Test successful user creation through admin interface"""
    # Get initial counts
    initial_user_count = db_session.query(User).count()
    initial_audit_count = db_session.query(AuditLog).count()
    initial_notif_count = db_session.query(Notification).count()

    # Get CSRF token
    response = client.get(url_for('admin.user.create'))
    csrf_token = extract_csrf_token(response.data)

    # Create test user data
    user_data = {
        'username': 'testuser_new',
        'email': 'testuser_new@example.com',
        'password': 'TestPass123!',
        'is_admin': False,
        'csrf_token': csrf_token
    }

    # Submit form
    response = client.post(
        url_for('admin.user.create'),
        data=user_data,
        follow_redirects=True
    )
    
    # Verify response
    assert response.status_code == 200
    assert b"User created successfully" in response.data

    # Verify database changes
    assert db_session.query(User).count() == initial_user_count + 1
    new_user = db_session.query(User).filter_by(username='testuser_new').first()
    assert new_user is not None
    assert new_user.email == 'testuser_new@example.com'
    assert new_user.check_password('TestPass123!')
    assert new_user.is_admin is False

    # Verify audit log
    assert db_session.query(AuditLog).count() == initial_audit_count + 1
    audit_log = db_session.query(AuditLog).order_by(AuditLog.id.desc()).first()
    assert audit_log.action == 'create_user'
    assert audit_log.object_type == 'User'
    assert audit_log.object_id == new_user.id
    assert audit_log.details_after is not None

    # Verify notification
    assert db_session.query(Notification).count() == initial_notif_count + 1
    notification = db_session.query(Notification).order_by(Notification.id.desc()).first()
    assert notification.type == 'user_created'
    assert notification.message == f"User testuser_new created successfully"
    assert notification.related_object_type == 'User'
    assert notification.related_object_id == new_user.id

def test_admin_create_user_validation_errors(logged_in_admin, client):
    """Test user creation validation errors"""
    # Get CSRF token
    response = client.get(url_for('admin.user.create'))
    csrf_token = extract_csrf_token(response.data)

    # Test missing required fields
    test_cases = [
        ({}, "Username is required"),
        ({'username': 'testuser'}, "Email is required"),
        ({'username': 'testuser', 'email': 'test@example.com'}, "Password is required"),
    ]

    for data, expected_error in test_cases:
        data['csrf_token'] = csrf_token
        response = client.post(
            url_for('admin.user.create'),
            data=data,
            follow_redirects=True
        )
        assert response.status_code == 400
        assert expected_error.encode() in response.data

    # Test duplicate username/email
    duplicate_cases = [
        ({'username': 'admin', 'email': 'new@example.com', 'password': 'TestPass123!'}, 
         "Username already exists"),
        ({'username': 'newuser', 'email': 'admin@example.com', 'password': 'TestPass123!'}, 
         "Email already exists"),
    ]

    for data, expected_error in duplicate_cases:
        data['csrf_token'] = csrf_token
        response = client.post(
            url_for('admin.user.create'),
            data=data,
            follow_redirects=True
        )
        assert response.status_code == 400
        assert expected_error.encode() in response.data

def test_admin_create_user_invalid_password(logged_in_admin, client):
    """Test password validation during user creation"""
    # Get CSRF token
    response = client.get(url_for('admin.user.create'))
    csrf_token = extract_csrf_token(response.data)

    # Test invalid passwords
    invalid_passwords = [
        ('short', "Password must be at least 8 characters"),
        ('no_uppercase1', "Password must contain at least one uppercase letter"),
        ('NO_LOWERCASE1', "Password must contain at least one lowercase letter"),
        ('NoNumbers', "Password must contain at least one number"),
    ]

    for password, expected_error in invalid_passwords:
        user_data = {
            'username': f'testuser_{password[:4]}',
            'email': f'testuser_{password[:4]}@example.com',
            'password': password,
            'csrf_token': csrf_token
        }
        response = client.post(
            url_for('admin.user.create'),
            data=user_data,
            follow_redirects=True
        )
        assert response.status_code == 400
        assert expected_error.encode() in response.data
