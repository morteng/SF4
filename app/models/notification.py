from flask import current_app
from app.extensions import db
from datetime import datetime
from sqlalchemy import ForeignKey
from app.constants import NotificationType, NotificationPriority

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
        self.read_status = True
        db.session.commit()
        return self

    @classmethod
    def get_unread_count(cls):
        return cls.query.filter_by(read_status=False).count()
