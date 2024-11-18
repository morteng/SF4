from sqlalchemy.ext.declarative import declarative_base
from .user import User
from .bot import Bot
from .notification import Notification
from .organization import Organization
from .stipend import Stipend
from .tag import Tag

Base = declarative_base()
