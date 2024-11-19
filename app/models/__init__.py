from flask_sqlalchemy import SQLAlchemy
from .bot import Bot
from .notification import Notification
from .organization import Organization
from .stipend import Stipend
from .tag import Tag
from .user import User
from .association_tables import init_association_tables

db = SQLAlchemy()

def init_models(db):
    global stipend_tag_association
    stipend_tag_association = init_association_tables(db)

def init_models(app):
    db.init_app(app)