from app.extensions import db
from datetime import datetime
from enum import Enum

class NotificationType(Enum):
    BOT_SUCCESS = 'bot_success'
    BOT_ERROR = 'bot_error'
    USER_ACTION = 'user_action'
    SYSTEM = 'system'

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(255), nullable=False)
    type = db.Column(db.Enum(NotificationType), nullable=False)
    read_status = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    related_object_type = db.Column(db.String(50))
    related_object_id = db.Column(db.Integer)

    def __repr__(self):
        return f"<Notification {self.id}: {self.message}>"

    def mark_as_read(self):
        self.read_status = True
        db.session.commit()

    @classmethod
    def get_unread_count(cls):
        return cls.query.filter_by(read_status=False).count()
