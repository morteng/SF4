from app.models.notification import Notification

def get_notification_by_id(notification_id):
    from app import db
    return db.session.get(Notification, notification_id)

def get_notification_count(user_id):
    """Get count of unread notifications for a user"""
    from app import db
    return db.session.query(Notification).filter_by(user_id=user_id, read_status=False).count()
