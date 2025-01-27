from app.models import Base
from app.extensions import db
from datetime import datetime
from sqlalchemy import ForeignKey
from app.common.enums import NotificationType, NotificationPriority
from flask import current_app
from app.models.user import User

class Notification(Base):
    __tablename__ = 'notification'
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(255), nullable=False)
    type = db.Column(db.Enum(NotificationType), nullable=False)
    read_status = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    related_object_type = db.Column(db.String(50))
    related_object_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, ForeignKey(User.id), nullable=True)
    priority = db.Column(db.Enum(NotificationPriority), default=NotificationPriority.MEDIUM)

    user = db.relationship(User, backref='notifications')

    def __init__(self, message, type, user_id=None, related_object_type=None, related_object_id=None):
        self.message = message
        self.type = type
        self.user_id = user_id
        self.related_object_type = related_object_type
        self.related_object_id = related_object_id

    def mark_as_read(self):
        self.read_status = True
        return self

    def __repr__(self):
        return f"Notification('{self.message}', '{self.type}', '{self.read_status}')"
