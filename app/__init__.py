from flask import Flask
from .extensions import db, migrate
from .config import get_config

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Load configuration using the get_config function
    config_class = get_config(config_name)
    if config_class:
        app.config.from_object(config_class)
    else:
        raise ValueError(f"Unknown configuration name: {config_name}")
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Register blueprints and other components here if needed
    
    return app
