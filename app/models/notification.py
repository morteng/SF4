from flask import current_app
from app.extensions import db
from datetime import datetime
from sqlalchemy import ForeignKey
from app.common.enums import NotificationType, NotificationPriority

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(255), nullable=False)
    type = db.Column(db.Enum(NotificationType), nullable=False)
    read_status = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    related_object_type = db.Column(db.String(50))
    related_object_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    priority = db.Column(db.Enum(NotificationPriority), default=NotificationPriority.MEDIUM)

    def __repr__(self):
        return f"<Notification {self.id}: {self.type} - {self.message}>"

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type.value,
            'message': self.message,
            'read_status': self.read_status,
            'created_at': self.created_at.isoformat(),
            'related_object_type': self.related_object_type,
            'related_object_id': self.related_object_id,
            'user_id': self.user_id,
            'priority': self.priority.value
        }

    def mark_as_read(self):
        """Mark notification as read with enhanced error handling"""
        if not self.id:
            raise ValueError("Cannot mark unsaved notification as read")
            
        try:
            self.read_status = True
            db.session.commit()
            return self
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error marking notification as read: {str(e)}")
            # Create audit log for the failed operation
            try:
                from app.models.audit_log import AuditLog
                AuditLog.create(
                    user_id=self.user_id,
                    action="notification_mark_read_failed",
                    object_type="Notification",
                    object_id=self.id,
                    details=str(e),
                    commit=True,
                    notify=False
                )
            except Exception as audit_error:
                current_app.logger.error(f"Failed to create audit log: {str(audit_error)}")
            raise ValueError("Failed to mark notification as read") from e

    @classmethod
    def get_unread_count(cls):
        return cls.query.filter_by(read_status=False).count()

    @classmethod
    def create(cls, type, message, user_id=None, related_object=None, **kwargs):
        """Create a new notification with error handling"""
        try:
            notification = cls(
                type=type,
                message=message,
                user_id=user_id,
                **kwargs
            )
            if related_object:
                notification.related_object_type = related_object.__class__.__name__
                notification.related_object_id = related_object.id
            db.session.add(notification)
            db.session.commit()
            return notification
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating notification: {str(e)}")
            raise ValueError(f"Failed to create notification: {str(e)}")
