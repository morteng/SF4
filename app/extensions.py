from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()

# Initialize login manager here
login_manager = LoginManager()

def init_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)  # Initialize login manager here
    login_manager.login_view = 'admin_auth.login'  # Set the login view for unauthorized access
