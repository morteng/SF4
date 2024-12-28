import logging
from app import db
from app.models.notification import Notification
from app.constants import NotificationType, NotificationPriority

logger = logging.getLogger(__name__)

def create_notification(type: NotificationType, message: str, user_id=None, related_object=None, priority=NotificationPriority.MEDIUM):
    """Create a new notification with validation"""
    if not isinstance(type, NotificationType):
        raise ValueError("Notification type must be a NotificationType enum")
    
    try:
        notification = Notification(
            type=type,
            message=message,
            user_id=user_id,
            priority=priority
        )
        
        if related_object:
            notification.related_object_type = related_object.__class__.__name__
            notification.related_object_id = related_object.id
            
        db.session.add(notification)
        db.session.commit()
        return notification
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating notification: {str(e)}")
        raise

def mark_notification_read(notification_id):
    """Mark a notification as read"""
    notification = Notification.query.get(notification_id)
    if not notification:
        raise ValueError("Notification not found")
    
    notification.read_status = True
    db.session.commit()
    return notification

def delete_notification(notification_id):
    """Delete a notification"""
    notification = Notification.query.get(notification_id)
    if not notification:
        raise ValueError("Notification not found")
    
    db.session.delete(notification)
    db.session.commit()
    return True

def get_notification_count(user_id):
    """Get count of unread notifications for a user"""
    try:
        if not user_id:
            raise ValueError("User ID is required")
            
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

def get_notification_by_id(notification_id):
    """Get a notification by its ID"""
    return db.session.get(Notification, notification_id)
