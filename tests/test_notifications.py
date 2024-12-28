import pytest
from app.models.notification import Notification
from app.services.notification_service import get_notification_count

def test_get_notification_count(client, db_session, test_user):
    # Create test notifications
    Notification.create(type="test", message="Test 1", user_id=test_user.id)
    Notification.create(type="test", message="Test 2", user_id=test_user.id)
    
    count = get_notification_count(test_user.id)
    assert count == 2

def test_get_notification_count_invalid_user(client, db_session):
    count = get_notification_count(None)
    assert count == 0

def test_get_notification_count_high_threshold(client, db_session, test_user, caplog):
    # Create more than 10 notifications
    for i in range(15):
        Notification.create(type="test", message=f"Test {i}", user_id=test_user.id)
    
    count = get_notification_count(test_user.id)
    assert count == 15
    assert "High notification count (15)" in caplog.text
