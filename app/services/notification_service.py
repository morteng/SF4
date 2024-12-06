from app.models.notification import Notification

def get_notification_by_id(notification_id):
    """Retrieve a notification by its ID."""
    from app import db
    return db.session.get(Notification, notification_id)
