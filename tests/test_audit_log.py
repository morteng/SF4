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
    password_hash = generate_password_hash("password123")
    user = User(username="testuser", email="test@example.com", password_hash=password_hash)
    db_session.add(user)
    db_session.commit()

    with client:
        # First make a GET request to establish session and get CSRF token
        # Use follow_redirects=True to handle any redirects automatically
        get_response = client.get(url_for('public.login'), follow_redirects=True)
        
        assert get_response.status_code == 200, f"Expected 200, got {get_response.status_code}"

        # Extract CSRF token using BeautifulSoup
        soup = BeautifulSoup(get_response.data.decode(), 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
        assert csrf_token, "CSRF token not found in form"

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
