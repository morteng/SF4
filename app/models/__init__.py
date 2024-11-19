from flask_sqlalchemy import SQLAlchemy

# Import the db instance from app.__init__.py
from .. import db

def init_models(app):
    # Register models with the app's db instance
    from .bot import Bot
    from .notification import Notification
    from .organization import Organization
    from .stipend import Stipend
    from .tag import Tag
    from .user import User
    
    # No need to reflect metadata here, as we are defining the models explicitly
