from app.models import Base
from app.extensions import db
from datetime import datetime
from sqlalchemy import ForeignKey
from app.common.enums import NotificationType, NotificationPriority
from flask import current_app
from app.models.user import User  # Add this import

class Notification(Base):
    __tablename__ = 'notification'
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(255), nullable=False)
    type = db.Column(db.Enum(NotificationType), nullable=False)
    read_status = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    related_object_type = db.Column(db.String(50))
    related_object_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=True)  # Ensure correct reference
    priority = db.Column(db.Enum(NotificationPriority), default=NotificationPriority.MEDIUM)

    # ... rest of the class remains unchanged ...
