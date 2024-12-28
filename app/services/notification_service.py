import logging
logger = logging.getLogger(__name__)
from app.models.notification import Notification

def get_notification_by_id(notification_id):
    from app import db
    return db.session.get(Notification, notification_id)

def create_crud_notification(action, object_type, object_id, user_id=None):
    """Create notification for CRUD operations"""
    message = f"{action.capitalize()} operation performed on {object_type} {object_id}"
    notification = Notification.create(
        type=NotificationType.CRUD_OPERATION,
        message=message,
        related_object=f"{object_type}:{object_id}",
        user_id=user_id
    )
    return notification

def get_notification_count(user_id):
    """Get count of unread notifications for a user"""
    from app import db
    try:
        count = db.session.query(Notification).filter(
            (Notification.user_id == user_id) |
            (Notification.user_id.is_(None)),  # Include system-wide notifications
            Notification.read_status == False
        ).count()
        
        # Log if count is high
        if count > 10:
            logger.warning(f"High notification count ({count}) for user {user_id}")
            
        return count
    except Exception as e:
        logger.error(f"Error getting notification count for user {user_id}: {str(e)}")
        return 0  # Return 0 to prevent template rendering issues
    finally:
        db.session.close()
