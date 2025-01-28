from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.configs import BaseConfig
from app.common.utils import configure_logging

db = SQLAlchemy()

def create_app(config_class=BaseConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize logging
    configure_logging(app)
    
    db.init_app(app)
    
    with app.app_context():
        # Import routes and initialize database
        from . import routes
        db.create_all()
        
    return app
