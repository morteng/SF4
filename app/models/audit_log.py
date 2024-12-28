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
        
        try:
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
                endpoint=endpoint
            )
            
            # Use context manager for session management
            with db.session.begin_nested():
                db.session.add(log)
                if commit:
                    db.session.commit()
                    
            logger.info(f"Created audit log: {action} by user {user_id}")
            return log
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating audit log: {str(e)}", exc_info=True)
            # Preserve the original exception type
            raise type(e)(f"Failed to create audit log: {str(e)}") from e
        
        try:
            # Validate required fields
            if not action:
                raise ValueError("Action is required")
            if not isinstance(action, str):
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
                endpoint=endpoint
            )
            
            # Use context manager for session management
            with db.session.begin_nested():
                db.session.add(log)
                if commit:
                    db.session.commit()
                    
            logger.info(f"Created audit log: {action} by user {user_id}")
            return log
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating audit log: {str(e)}", exc_info=True)
            # Preserve the original exception type
            raise type(e)(f"Failed to create audit log: {str(e)}") from e
            
        # Validate and serialize complex data
        if details_before and not isinstance(details_before, (dict, str)):
            raise ValueError("details_before must be dict or JSON string")
        if details_after and not isinstance(details_after, (dict, str)):
            raise ValueError("details_after must be dict or JSON string")
            
        try:
            # Create audit log
            log = AuditLog(
                user_id=user_id,
                action=action,
                details=details,
                object_type=object_type,
                object_id=object_id,
                details_before=json.dumps(details_before) if isinstance(details_before, dict) else details_before,
                details_after=json.dumps(details_after) if isinstance(details_after, dict) else details_after,
                ip_address=ip_address,
                http_method=http_method,
                endpoint=endpoint,
                timestamp=datetime.now(timezone.utc)
            )
            
            db.session.add(log)
            if commit:
                db.session.commit()
            
            # Create notification if needed
            if notify and object_type != 'Notification':
                try:
                    Notification = get_notification_model()
                    Notification.create(
                        type=NotificationType.AUDIT_LOG,
                        message=f"{action.capitalize()} operation on {object_type} {object_id}",
                        related_object=log,
                        user_id=user_id
                    )
                except Exception as e:
                    current_app.logger.error(f"Error creating notification for audit log: {str(e)}")
            
            return log
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating audit log: {str(e)}")
            raise
        
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
            http_method=http_method,
            endpoint=endpoint,
            timestamp=datetime.now(timezone.utc)
        )
        db.session.add(log)
        if commit:
            db.session.commit()
        
        # Create notification if this isn't being called from Notification.create()
        if object_type != 'Notification':
            Notification = get_notification_model()
            Notification.create(
                type=NotificationType.AUDIT_LOG,
                message=f"{action.capitalize()} operation on {object_type} {object_id}",
                related_object=log,
                user_id=user_id
            )
        
        return log
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
                http_method=http_method,
                endpoint=endpoint,
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
