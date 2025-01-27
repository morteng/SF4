from app.database import db

class Base(db.Model):
    __abstract__ = True

__all__ = [
    'Base',
    'db',
    'User',
    'Stipend',
    'Notification',
    'AuditLog',
    'Tag',
    'Bot'
]
