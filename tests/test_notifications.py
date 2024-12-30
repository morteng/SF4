import pytest
from app.models.notification import Notification, NotificationType
from app.services.notification_service import (
    create_notification,
    mark_notification_read,
    delete_notification
)
from app.models.user import User
from app.extensions import db

def test_notification_lifecycle(client, db_session, test_user):
    # Create notification
    notification = create_notification(
        type=NotificationType.INFO,
        message="Test notification",
        user_id=test_user.id
    )
    assert notification.id is not None
    assert notification.read_status is False
    
    # Mark as read
    mark_notification_read(notification.id)
    db_session.refresh(notification)
    assert notification.read_status is True
    
    # Delete notification
    delete_notification(notification.id)
    assert Notification.query.get(notification.id) is None
