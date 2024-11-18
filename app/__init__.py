from flask import Flask
from .routes import register_blueprints

def create_app(config_name=None):
    app = Flask(__name__)
    
    # Load configuration
    config_class = get_config(config_name or 'default')
    app.config.from_object(config_class)
    
    # Initialize extensions (if any)
    initialize_extensions(app)
    
    # Register blueprints
    register_blueprints(app)
    
    return app

def get_config(config_name):
    if config_name == 'default':
        from .config.default import DefaultConfig
        return DefaultConfig
    elif config_name == 'development':
        from .config.development import DevelopmentConfig
        return DevelopmentConfig
    elif config_name == 'testing':
        from .config.testing import TestingConfig
        return TestingConfig
    elif config_name == 'production':
        from .config.production import ProductionConfig
        return ProductionConfig
    else:
        from .config.default import DefaultConfig
        return DefaultConfig

def initialize_extensions(app):
    # Initialize your extensions here (e.g., db, migrate)
    from .extensions import db, migrate
    db.init_app(app)
    migrate.init_app(app, db)
