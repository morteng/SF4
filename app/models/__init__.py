from .user import User
from .bot import Bot
from .notification import Notification
from .organization import Organization
from .stipend import Stipend
from .tag import Tag

def init_models(app):
    from app.extensions import db
    with app.app_context():
        db.create_all()
