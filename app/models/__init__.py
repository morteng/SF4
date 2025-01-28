from app.database import db

class Base(db.Model):
    __abstract__ = True

from .organization import Organization
from .stipend import Stipend
from .notification import Notification
from .audit_log import AuditLog
from .tag import Tag
from .bot import Bot
from .user import User

__all__ = [
    'Base',
    'db',
    'User',
    'Stipend',
    'Notification',
    'AuditLog',
    'Tag',
    'Bot',
    'Organization'
]
