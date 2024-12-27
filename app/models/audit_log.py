from datetime import datetime
from app.extensions import db

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
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
        log = AuditLog(
            user_id=user_id,
            action=action,
            details=details,
            object_type=object_type,
            object_id=object_id,
            details_before=details_before,
            details_after=details_after,
            ip_address=ip_address
        )
        db.session.add(log)
        db.session.commit()
        return log
