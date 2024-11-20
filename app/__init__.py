from flask import Flask
from config import Config
from app.extensions import db, login_manager  # Import login_manager here

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    init_extensions(app)

    # Register blueprints
    from app.routes.admin import admin_bp
    from app.routes.public_bot_routes import public_bot_bp
    from app.routes.public_user_routes import public_user_bp
    from app.routes.public_routes import public_bp  # Ensure this is imported

    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(public_bot_bp)
    app.register_blueprint(public_user_bp)
    app.register_blueprint(public_bp)  # Register the public blueprint

    return app

def init_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)  # Initialize login manager here
    login_manager.login_view = 'admin_auth.login'  # Set the login view for unauthorized access

# Import and initialize LoginManager
from flask_login import LoginManager
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    return User.query.get(int(user_id))
