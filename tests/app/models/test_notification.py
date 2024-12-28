import pytest
import uuid
from app.models.notification import Notification
from app.models.user import User
from datetime import datetime
from app.constants import NotificationType, NotificationPriority

@pytest.fixture
def test_notification(db_session):
    """Provide a test notification"""
    # Use unique identifiers for each test run
    unique_id = str(uuid.uuid4())[:8]
    user = User(
        username=f'testuser_{unique_id}', 
        email=f'test_{unique_id}@example.com',
        password_hash='testpasswordhash'
    )
    db_session.add(user)
    db_session.commit()
    
    notification = Notification(
        message='Test notification',
        type=NotificationType.SYSTEM,
        user_id=user.id,
        priority=NotificationPriority.MEDIUM
    )
    db_session.add(notification)
    db_session.commit()
    yield notification
    
    # Clean up both notification and user
    db_session.delete(notification)
    db_session.delete(user)
    db_session.commit()

def test_notification_creation(test_notification):
    """Test notification creation"""
    assert test_notification.id is not None
    assert test_notification.message == 'Test notification'
    assert test_notification.type == NotificationType.SYSTEM
    assert test_notification.priority == NotificationPriority.MEDIUM

def test_mark_as_read(test_notification):
    """Test marking notification as read"""
    assert test_notification.read_status is False
    test_notification.mark_as_read()
    assert test_notification.read_status is True

def test_notification_to_dict(test_notification):
    """Test notification serialization"""
    notification_dict = test_notification.to_dict()
    assert notification_dict['message'] == 'Test notification'
    assert notification_dict['type'] == NotificationType.SYSTEM.value
    assert notification_dict['priority'] == NotificationPriority.MEDIUM.value
    assert 'created_at' in notification_dict
    assert notification_dict['read_status'] is False

def test_audit_log_rollback(db_session):
    """Test audit log rollback on error"""
    from app.models.audit_log import AuditLog
    from sqlalchemy.exc import IntegrityError
    
    # Create invalid audit log (missing required action)
    with pytest.raises(ValueError):
        AuditLog.create(user_id=1, action=None)
    
    # Verify no audit log was created
    assert db_session.query(AuditLog).count() == 0

def test_audit_log_error_handling(db_session):
    """Test audit log error handling"""
    from app.models.audit_log import AuditLog
    
    # Create audit log with invalid data
    with pytest.raises(ValueError):
        AuditLog.create(
            user_id=1,
            action='test',
            object_type='Test',
            object_id=None  # Missing required object_id
        )
    
    # Verify no audit log was created
    assert db_session.query(AuditLog).count() == 0
