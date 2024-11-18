import os
from flask import Flask
from config import get_config
from .extensions import db, migrate  # Ensure you have the migrate extension defined
from dotenv import load_dotenv  # Import load_dotenv from python-dotenv

def create_app(config_name=None):
    # Load environment variables from .env file
    load_dotenv()

    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')
    
    config = get_config(config_name)
    
    app = Flask(__name__)
    app.config.from_object(config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Import models to ensure they are registered with SQLAlchemy
    from .models import user, stipend, tag, organization, bot, notification, association_tables

    # Register routes
    from .routes.public_user_routes import public_user_bp
    from .routes.admin_routes import admin_bp
    from .routes.public_bot_routes import public_bot_bp as bot_bp  # Ensure this is correctly referencing the blueprint
    
    app.register_blueprint(public_user_bp)  # Ensure the blueprint is correctly referenced
    app.register_blueprint(admin_bp)  # Ensure the blueprint is correctly referenced
    app.register_blueprint(bot_bp)  # Register the bot blueprint

    return app
