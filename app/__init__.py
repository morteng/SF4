from flask import Flask
from .extensions import db, migrate
from .routes import register_blueprints
from . import config

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Load configuration
    if config_name == 'development':
        app.config.from_object(config.DevelopmentConfig)
    elif config_name == 'testing':
        app.config.from_object(config.TestingConfig)
    elif config_name == 'production':
        app.config.from_object(config.ProductionConfig)
    else:
        raise ValueError(f"Unknown configuration name: {config_name}")

    # Initialize database
    db.init_app(app)

    # Initialize migrate
    migrate.init_app(app, db)

    # Register blueprints
    register_blueprints(app)

    return app
