from flask import Flask
from .extensions import db, migrate
from .routes import register_blueprints

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)

    # Initialize database
    db.init_app(app)

    # Initialize migrate
    migrate.init_app(app, db)

    # Register blueprints
    register_blueprints(app)

    return app

def get_config(config_name):
    if config_name == 'development':
        from .config import DevelopmentConfig
        return DevelopmentConfig()
    elif config_name == 'testing':
        from .config import TestingConfig
        return TestingConfig()
    elif config_name == 'production':
        from .config import ProductionConfig
        return ProductionConfig()
    else:
        raise ValueError(f"Unknown configuration name: {config_name}")
