from flask import Flask
from .extensions import db, migrate
from .routes import register_blueprints
from .config import get_config

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Load configuration
    config = get_config(config_name)
    if config:
        app.config.from_object(config)
    else:
        raise ValueError(f"Unknown configuration name: {config_name}")

    # Initialize database
    db.init_app(app)

    # Initialize migrate
    migrate.init_app(app, db)

    # Register blueprints
    register_blueprints(app)

    return app
