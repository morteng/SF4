from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models
from .user import User
from .stipend import Stipend
from .tag import Tag
from .organization import Organization
from .bot import Bot
from .notification import Notification
from .association_tables import init_association_tables, stipend_tags, stipend_organizations

# Initialize association tables after db is set up
init_association_tables(db)
