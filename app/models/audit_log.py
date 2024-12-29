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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    object_type = db.Column(db.String(50), nullable=True)
    object_id = db.Column(db.Integer, nullable=True)
    details = db.Column(db.Text, nullable=True)
    details_before = db.Column(db.Text, nullable=True)
    details_after = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    http_method = db.Column(db.String(10), nullable=True)
    endpoint = db.Column(db.String(100), nullable=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    @staticmethod
    def create(user_id, action, details=None, object_type=None, object_id=None,
              details_before=None, details_after=None, ip_address=None,
              http_method=None, endpoint=None, commit=True, notify=True):
        """Create audit log entry with enhanced error handling and logging"""
        logger = logging.getLogger(__name__)
        
        # Ensure audit_log table exists
        if not db.inspect(db.engine).has_table('audit_log'):
            logger.error("Audit log table does not exist")
            raise RuntimeError("Audit log table not found")
            
        try:
            logger.info(f"Creating audit log: {action} by user {user_id}")
            
            # Validate required fields
            if not action:
                logger.error("Attempt to create audit log without action")
                raise ValueError("Action is required")
            if not isinstance(action, str):
                logger.error(f"Invalid action type: {type(action)}")
                raise TypeError("Action must be a string")
            
            # Validate object type/id relationship
            if object_type and not object_id:
                raise ValueError("object_id is required when object_type is provided")
            if object_id and not object_type:
                raise ValueError("object_type is required when object_id is provided")
            
            # Validate string lengths
            if action and len(action) > 100:
                raise ValueError("Action exceeds maximum length of 100 characters")
            if object_type and len(object_type) > 50:
                raise ValueError("Object type exceeds maximum length of 50 characters")
            
            # Validate and serialize complex data
            if details_before and not isinstance(details_before, (dict, str)):
                raise ValueError("details_before must be dict or JSON string")
            if details_after and not isinstance(details_after, (dict, str)):
                raise ValueError("details_after must be dict or JSON string")
            
            # Convert dictionaries to JSON strings
            if isinstance(details_before, dict):
                details_before = json.dumps(details_before)
            if isinstance(details_after, dict):
                details_after = json.dumps(details_after)

            # Create the audit log entry
            log = AuditLog(
                user_id=user_id,
                action=action,
                details=details,
                object_type=object_type,
                object_id=object_id,
                details_before=details_before,
                details_after=details_after,
                ip_address=ip_address,
                http_method=http_method,
                endpoint=endpoint,
                timestamp=datetime.now(timezone.utc)
            )
            
            # Use context manager for session management
            with db.session.begin_nested():
                db.session.add(log)
                if commit:
                    db.session.commit()
            
            # Create notification if needed
            if notify and object_type != 'Notification':
                try:
                    Notification = get_notification_model()
                    Notification.create(
                        type=NotificationType.AUDIT_LOG.value,
                        message=f"{action.capitalize()} operation on {object_type} {object_id}",
                        user_id=user_id,
                        related_object=log
                    )
                except Exception as e:
                    current_app.logger.error(f"Error creating notification for audit log: {str(e)}")
            
            logger.info(f"Created audit log: {action} by user {user_id}")
            return log
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating audit log: {str(e)}", exc_info=True)
            raise
