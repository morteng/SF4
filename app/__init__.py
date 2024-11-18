from flask import Flask
import os  # Import the os module
from .config import get_config  # Use get_config function instead of importing Config directly
from app.extensions import db

def create_app(config_name='default'):
    # Create and configure the app
    app = Flask(__name__)
    
    # Load configuration based on environment variable or default to 'default'
    config_class = get_config(config_name)
    app.config.from_object(config_class)

    # Print the configuration class being used
    print(f"Loaded configuration: {config_class.__name__}")

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    from app.routes.admin import admin_bp
    from app.routes.user import user_bp
    from app.routes.public_bot_routes import public_bot_bp
    from app.routes.public_user_routes import public_user_bp

    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(public_bot_bp, url_prefix='/bot')
    app.register_blueprint(public_user_bp, url_prefix='/user')

    return app
