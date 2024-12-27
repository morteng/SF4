from datetime import datetime
from app.extensions import db

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(100), nullable=False)
    object_type = db.Column(db.String(50))
    object_id = db.Column(db.Integer)
    details_before = db.Column(db.Text)
    details_after = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    @staticmethod
    def create(user_id, action, details):
        log = AuditLog(
            user_id=user_id,
            action=action,
            details=details
        )
        db.session.add(log)
        return log