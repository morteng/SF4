from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()

def init_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
