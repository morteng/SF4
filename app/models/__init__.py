from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_models(app):
    from .bot import Bot
    from .notification import Notification
    from .organization import Organization
    from .stipend import Stipend
    from .tag import Tag
    from .user import User
    
    # Register models with the app's db instance
    db.Model.metadata.reflect(bind=app.db.engine)
