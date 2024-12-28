import logging
import json
from datetime import datetime, timezone
from flask import current_app
from app.extensions import db
from app.models.notification import Notification

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
            
            # Create notification
            Notification.create(
                type='audit_log',
                message=f"{action.capitalize()} operation on {object_type} {object_id}",
                related_object=log,
                user_id=user_id
            )
            
            return log
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating audit log: {str(e)}")
            raise
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating audit log: {str(e)}")
            notification = Notification(
                message=f"Error creating audit log: {str(e)}",
                type="system",
                read_status=False,
                user_id=user_id if user_id else 0
            )
            db.session.add(notification)
            db.session.commit()
            raise
        """Create an audit log entry with before/after state tracking"""
        try:
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
            
            # Create appropriate notification based on action type
            from app.models.notification import Notification, NotificationType
            notification_type = {
                'create': NotificationType.CRUD_CREATE,
                'update': NotificationType.CRUD_UPDATE,
                'delete': NotificationType.CRUD_DELETE
            }.get(action.split('_')[0], NotificationType.SYSTEM)
            
            notification = Notification(
                message=f"{action.capitalize()} operation on {object_type} {object_id}",
                type=notification_type,
                read_status=False,
                user_id=user_id,
                related_object_type=object_type,
                related_object_id=object_id
            )
            db.session.add(notification)
            
            db.session.commit()
            return log
        except Exception as e:
            # Log error and create notification
            logger.error(f"Error creating audit log: {str(e)}")
            notification = Notification(
                message=f"Error creating audit log: {str(e)}",
                type="system",
                read_status=False
            )
            db.session.add(notification)
            db.session.commit()
            raise
