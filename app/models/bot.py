from datetime import datetime
from app.extensions import db  # Import the shared db instance

class Bot(db.Model):
    __tablename__ = 'bots'

    bot_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(255))
    status = db.Column(db.String(50), default='inactive')
    last_run = db.Column(db.DateTime, default=datetime.utcnow)
    error_log = db.Column(db.Text)

    def __repr__(self):
        return f"<Bot(name={self.name}, status={self.status})>"
