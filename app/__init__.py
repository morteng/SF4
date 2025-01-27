from flask import Flask
from app.configs.base_config import BaseConfig
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(config_class=BaseConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    
    with app.app_context():
        # Import routes and initialize database
        from . import routes
        db.create_all()
        
    return app
