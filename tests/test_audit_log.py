import pytest
from bs4 import BeautifulSoup
from werkzeug.security import generate_password_hash
from flask import url_for
from app.models.audit_log import AuditLog
from app.models.user import User

def test_audit_log_creation(client, db_session, test_user):
    log = AuditLog.create(
        user_id=test_user.id,
        action="test_action",
        details="Test details"
    )
    assert log.id is not None
    assert log.action == "test_action"

def test_audit_log_missing_action(client, db_session, test_user):
    with pytest.raises(ValueError):
        AuditLog.create(
            user_id=test_user.id,
            action=None
        )

def test_audit_log_object_type_without_id(client, db_session, test_user):
    with pytest.raises(ValueError):
        AuditLog.create(
            user_id=test_user.id,
            action="test_action",
            object_type="TestType"
        )

def test_profile_update_creates_audit_log(client, db_session):
    """Test that profile updates create audit logs"""
    # Create test user
    user = User(
        username="testuser", 
        email="test@example.com", 
        password="password123"  # Use password instead of password_hash
    )
    db_session.add(user)
    db_session.commit()

    with client:
        # First make a GET request to establish session and get CSRF token
        # Use follow_redirects=True to handle any redirects automatically
        get_response = client.get(url_for('public.login'), follow_redirects=True)
        
        assert get_response.status_code == 200, f"Expected 200, got {get_response.status_code}"

        # Extract CSRF token using BeautifulSoup with error handling
        soup = BeautifulSoup(get_response.data.decode(), 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrf_token'})
        assert csrf_input is not None, "CSRF token input not found in form"
        csrf_token = csrf_input.get('value')
        assert csrf_token, "CSRF token value is empty"

        # Login user
        login_response = client.post(url_for('public.login'), data={
            'username': 'testuser',
            'password': 'password123',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        assert login_response.status_code == 200, "Login failed"

        # Clear any existing audit logs from login
        AuditLog.query.delete()
        db_session.commit()

        # Get CSRF token from the profile edit page
        get_response = client.get(url_for('user.edit_profile'))
        assert get_response.status_code == 200, "Failed to access profile edit page"
        soup = BeautifulSoup(get_response.data.decode(), 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
        assert csrf_token, "CSRF token not found in profile form"

        # Submit profile update and follow redirect
        response = client.post(url_for('user.edit_profile'), data={
            'username': 'newusername',
            'email': 'newemail@example.com',
            'csrf_token': csrf_token
        }, follow_redirects=True)

        # Verify successful update
        assert response.status_code == 200, "Profile update failed"
        assert b"Profile updated successfully" in response.data

        # Verify audit log was created
        audit_log = AuditLog.query.filter_by(user_id=user.id).first()
        assert audit_log is not None, "Audit log not created"
        assert audit_log.action == "profile_update", "Incorrect audit log action"
        assert "newusername" in audit_log.details, "Username not in audit log details"
        assert "newemail@example.com" in audit_log.details, "Email not in audit log details"
def test_audit_log_notification_creation(client, db_session, test_user):
    """Test that audit log creates proper notification"""
    log = AuditLog.create(
        user_id=test_user.id,
        action="test_action",
        details="Test details",
        notify=True
    )
    
    # Verify notification was created
    notification = Notification.query.filter_by(
        type=NotificationType.AUDIT_LOG,
        related_object=log
    ).first()
    
    assert notification is not None
    assert notification.message == "Test_action operation on None None"
