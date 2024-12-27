import logging
from app.models.notification import Notification

def get_notification_by_id(notification_id):
    from app import db
    return db.session.get(Notification, notification_id)

def get_notification_count(user_id):
    """Get count of unread notifications for a user"""
    from app import db
    try:
        count = db.session.query(Notification).filter(
            (Notification.user_id == user_id) |
            (Notification.user_id.is_(None)),  # Include system-wide notifications
            Notification.read_status == False
        ).count()
        return count
    except Exception as e:
        logging.error(f"Error getting notification count for user {user_id}: {str(e)}")
        return 0  # Return 0 to prevent template rendering issues
    finally:
        db.session.close()
