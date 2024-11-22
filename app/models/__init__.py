from app.extensions import db

def init_models(app):
    from .user import User
    from .stipend import Stipend
    from .tag import Tag
    from .organization import Organization
    from .bot import Bot
    from .notification import Notification
    # Other models can be imported here if needed
