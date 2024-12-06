from app.extensions import db
from datetime import datetime

class Notification(db.Model):
    """Notification model representing a message to be displayed to users."""
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    read_status = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        """Return a string representation of the Notification object."""
        return f"<Notification {self.message}>"
