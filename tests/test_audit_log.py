import pytest
from bs4 import BeautifulSoup
from werkzeug.security import generate_password_hash
from flask import url_for
from app.models.audit_log import AuditLog
from app.models.user import User
from app.models.notification import Notification
from app.constants import NotificationType

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

def test_audit_log_with_object_id(client, db_session, test_user):
    """Test audit log creation with object ID"""
    log = AuditLog.create(
        user_id=test_user.id,
        action="test_action",
        details="Test details",
        object_type="TestType",
        object_id=123
    )
    assert log.object_type == "TestType"
    assert log.object_id == 123

def test_audit_log_notification_details(client, db_session, test_user):
    """Test notification details format"""
    log = AuditLog.create(
        user_id=test_user.id,
        action="test_action",
        details="Test details",
        object_type="TestType",
        object_id=123,
        notify=True
    )
    
    notification = Notification.query.filter_by(
        type=NotificationType.AUDIT_LOG,
        related_object_type='AuditLog',
        related_object_id=log.id
    ).first()
    
    assert "Test_action operation on TestType 123" in notification.message
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
