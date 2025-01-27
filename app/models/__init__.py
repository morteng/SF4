from sqlalchemy import declarative_base

# Create the base class for declarative models
db = declarative_base()

# Import your models here
from .tag import Tag
from .user import User
from .audit_log import AuditLog
from .notification import Notification
from .stipend import Stipend
