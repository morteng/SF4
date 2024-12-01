from flask import Flask
from app.extensions import db, login_manager
from app.config import config_by_name
from dotenv import load_dotenv
import os

def create_app(config_name=None, instance_path=None):
    # Load environment variables from .env file
    load_dotenv()
    
    # Determine the config name from environment variable or default to 'development'
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'development')
    
    app = Flask(__name__, instance_path=instance_path)
    app.config.from_object(config_by_name[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Register admin blueprint
    from app.routes.admin import admin_bp
    app.register_blueprint(admin_bp)
    
    return app
