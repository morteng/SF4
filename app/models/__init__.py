from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from .bot import Bot
from .notification import Notification
from .organization import Organization
from .stipend import Stipend
from .tag import Tag
from .user import User
