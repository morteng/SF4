from app.models.notification import Notification
from app.extensions import db

def get_all_notifications():
    return Notification.query.all()

def get_notification_by_id(notification_id):
    return Notification.query.get(notification_id)

def create_notification(message, type='info', read_status=False):
    notification = Notification(message=message, type=type, read_status=read_status)
    db.session.add(notification)
    db.session.commit()
    return notification

def update_notification(notification_id, message=None, type=None, read_status=None):
    notification = get_notification_by_id(notification_id)
    if not notification:
        raise ValueError("Notification not found")
    
    if message is not None:
        notification.message = message
    if type is not None:
        notification.type = type
    if read_status is not None:
        notification.read_status = read_status
    
    db.session.commit()
    return notification

def delete_notification(notification_id):
    notification = get_notification_by_id(notification_id)
    if not notification:
        raise ValueError("Notification not found")
    
    db.session.delete(notification)
    db.session.commit()
