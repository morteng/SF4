import logging
import json
from datetime import datetime, timezone
from app.constants import NotificationType
from flask import current_app
from app.extensions import db

# Lazy import to avoid circular dependency
def get_notification_model():
    from app.models.notification import Notification
    return Notification

logger = logging.getLogger(__name__)

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    object_type = db.Column(db.String(50), nullable=True)
    object_id = db.Column(db.Integer, nullable=True)
    details = db.Column(db.Text, nullable=True)
    details_before = db.Column(db.Text, nullable=True)
    details_after = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    @staticmethod
    def create(user_id, action, details=None, object_type=None, object_id=None,
              details_before=None, details_after=None, ip_address=None):
        """Create audit log with JSON serialization and validation"""
        if details_before and not isinstance(details_before, (dict, str)):
            raise ValueError("details_before must be dict or JSON string")
        if details_after and not isinstance(details_after, (dict, str)):
            raise ValueError("details_after must be dict or JSON string")
        """Create audit log entry with before/after state tracking"""
        try:
            # Serialize dictionaries to JSON
            if isinstance(details_before, dict):
                details_before = json.dumps(details_before)
            if isinstance(details_after, dict):
                details_after = json.dumps(details_after)
            
            # Create audit log
            log = AuditLog(
                user_id=user_id,
                action=action,
                details=details,
                object_type=object_type or 'User',
                object_id=object_id,
                details_before=details_before,
                details_after=details_after,
                ip_address=ip_address,
                timestamp=datetime.now(timezone.utc)
            )
            db.session.add(log)
            db.session.commit()
            
            # Only create notification if this isn't being called from Notification.create()
            if object_type != 'Notification':
                Notification = get_notification_model()
                Notification.create(
                    type=NotificationType.AUDIT_LOG,
                    message=f"{action.capitalize()} operation on {object_type} {object_id}",
                    related_object=log,
                    user_id=user_id
                )
            
            return log
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating audit log: {str(e)}")
            raise
from datetime import datetime
from app.extensions import db

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    action_type = db.Column(db.String(50), nullable=False)
    object_type = db.Column(db.String(50), nullable=False)
    object_id = db.Column(db.Integer, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(50))
    http_method = db.Column(db.String(10))
    endpoint = db.Column(db.String(100))
    before_state = db.Column(db.Text, nullable=True)
    after_state = db.Column(db.Text, nullable=True)
