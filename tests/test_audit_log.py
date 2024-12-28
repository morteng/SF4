import pytest
from app.models.audit_log import AuditLog

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
