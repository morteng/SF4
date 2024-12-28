import pytest
from app.models.notification import Notification, NotificationType
from app.services.notification_service import (
    get_notification_count,
    create_notification,
    mark_notification_read,
    delete_notification
)
from app.models.user import User
from app.models.stipend import Stipend
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

def test_notification_with_related_object(client, db_session, test_user, test_stipend):
    # Create notification with related stipend
    notification = create_notification(
        type=NotificationType.WARNING,
        message="Stipend update",
        user_id=test_user.id,
        related_object=test_stipend
    )
    assert notification.related_object == test_stipend

def test_notification_error_handling(client, db_session):
    # Test invalid notification creation
    with pytest.raises(ValueError):
        create_notification(type="invalid", message="Test")
        
    # Test marking non-existent notification as read
    with pytest.raises(ValueError):
        mark_notification_read(99999)
        
    # Test deleting non-existent notification
    with pytest.raises(ValueError):
        delete_notification(99999)

def test_notification_count_edge_cases(client, db_session):
    # Test count with no notifications
    assert get_notification_count(None) == 0
    
    # Test count with invalid user
    assert get_notification_count(99999) == 0

def test_notification_priority_handling(client, db_session, test_user):
    # Test different priority levels
    for priority in ['low', 'medium', 'high']:
        notification = create_notification(
            type=NotificationType.INFO,
            message=f"Test {priority} priority",
            user_id=test_user.id,
            priority=priority
        )
        assert notification.priority == priority

def test_notification_type_validation(client, db_session, test_user):
    # Test valid notification types
    for ntype in NotificationType:
        notification = create_notification(
            type=ntype,
            message=f"Test {ntype.value}",
            user_id=test_user.id
        )
        assert notification.type == ntype

def test_crud_notification_creation(client, db_session, test_user):
    from app.services.notification_service import create_crud_notification
    
    # Test CRUD notification creation
    notification = create_crud_notification(
        action="create",
        object_type="TestObject",
        object_id=123,
        user_id=test_user.id
    )
    
    assert notification.type == NotificationType.CRUD_OPERATION
    assert "Create operation performed on TestObject 123" in notification.message
