from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from configs.config import Configuration

db = SQLAlchemy()

def create_app(config_class=Configuration):
    app = Flask(__name__)
    config = config_class()
    app.config.from_object(config)
    
    # Initialize configuration
    if hasattr(config, 'init_app'):
        config.init_app(app)
    
    # Configure logging
    config.configure_logging()
    
    db.init_app(app)
    
    with app.app_context():
        from . import routes
        db.create_all()
        
    return app
