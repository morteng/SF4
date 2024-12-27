import logging
from datetime import timezone
from datetime import datetime
from app.extensions import db

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
                timestamp=datetime.now(timezone.utc)  # Use timezone-aware datetime
            )
            db.session.add(log)
            
            # Create notification for audit log creation
            from app.models.notification import Notification
            notification = Notification(
                message=f"Audit log created for {action} on {object_type} {object_id}",
                type="system",
                read_status=False,
                user_id=user_id
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
