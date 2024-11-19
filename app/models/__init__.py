from .user import User
from .organization import Organization
from .stipend import Stipend
from .tag import Tag
from .bot import Bot
from .notification import Notification

def init_models(app):
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy(app)  # Ensure db is initialized here if not already done
