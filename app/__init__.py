from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.configs.base_config import BaseConfig
from logging_config import configure_logging

db = SQLAlchemy()

def create_app(config_class=BaseConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize configuration
    if hasattr(config_class, 'init_app'):
        config_class.init_app(app)
    
    # Configure logging
    configure_logging(app)
    
    db.init_app(app)
    
    with app.app_context():
        from . import routes
        db.create_all()
        
    return app
