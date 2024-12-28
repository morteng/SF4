import pytest
from app.models.notification import Notification
from app.models.user import User
from datetime import datetime
from app.constants import NotificationType, NotificationPriority

@pytest.fixture
def test_notification(db_session):
    """Provide a test notification"""
    user = User(
        username='testuser', 
        email='test@example.com',
        password_hash='testpasswordhash'  # Add required field
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
    db_session.delete(notification)
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
    assert notification_dict['type'] == NotificationType.INFO.value
    assert notification_dict['priority'] == NotificationPriority.MEDIUM.value
