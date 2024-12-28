from app.extensions import db
from datetime import datetime
from enum import Enum
from sqlalchemy import ForeignKey

class NotificationType(Enum):
    BOT_SUCCESS = 'bot_success'
    BOT_ERROR = 'bot_error'
    USER_ACTION = 'user_action'
    SYSTEM = 'system'
    CRUD_CREATE = 'crud_create'
    CRUD_UPDATE = 'crud_update'
    CRUD_DELETE = 'crud_delete'

class NotificationPriority(Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(255), nullable=False)
    type = db.Column(db.Enum(NotificationType), nullable=False)
    read_status = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    related_object_type = db.Column(db.String(50))
    related_object_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

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
            'user_id': self.user_id
        }

    def mark_as_read(self):
        self.read_status = True
        db.session.commit()

    @classmethod
    def get_unread_count(cls):
        return cls.query.filter_by(read_status=False).count()
        
    @classmethod
    def create(cls, type, message, related_object=None, user_id=None):
        notification = cls(
            type=type,
            message=message,
            read_status=False,
            user_id=user_id if user_id is not None else 0  # Default to system user
        )
        if related_object:
            notification.related_object_type = related_object.__class__.__name__
            notification.related_object_id = related_object.id
            if user_id is None and hasattr(related_object, 'user_id'):
                notification.user_id = related_object.user_id
        db.session.add(notification)
        db.session.commit()
        return notification
