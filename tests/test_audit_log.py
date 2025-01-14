import pytest
from bs4 import BeautifulSoup
from werkzeug.security import generate_password_hash
from flask import url_for
from app.models.audit_log import AuditLog
from app.models.user import User
from app.models.notification import Notification
from app.constants import NotificationType

def test_audit_log_creation(client, db_session, test_user):
    """Test audit log creation"""
    log = AuditLog.create(
        user_id=test_user.id,
        action="test_action",
        details="Test details"
    )
    assert log.id is not None
    assert log.action == "test_action"
    assert log.user_id == test_user.id
    assert log.details == "Test details"

def test_audit_log_missing_action(client, db_session, test_user):
    """Test audit log creation with missing required field"""
    with pytest.raises(ValueError):
        AuditLog.create(
            user_id=test_user.id,
            action=None
        )

def test_audit_log_object_type_without_id(client, db_session, test_user):
    """Test audit log creation with object type but no ID"""
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

