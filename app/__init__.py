from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.configs.base import BaseConfig

db = SQLAlchemy()

def create_app(config_class=BaseConfig):
    app = Flask(__name__)
    config = config_class(app.root_path)
    app.config.from_object(config)
    
    # Initialize configuration
    if hasattr(config, 'init_app'):
        config.init_app(app)
    
    db.init_app(app)
    
    with app.app_context():
        from . import routes
        db.create_all()
        
    return app
