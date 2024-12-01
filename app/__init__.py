from flask import Flask
from app.extensions import db, login_manager
from app.config import config_by_name

def create_app(config_name, instance_path=None):
    app = Flask(__name__, instance_path=instance_path)
    app.config.from_object(config_by_name[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Register blueprints or other setup
    
    return app
