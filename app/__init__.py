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
    from .config import DefaultConfig, DevelopmentConfig, TestingConfig, ProductionConfig
    
    config_map = {
        'default': DefaultConfig,
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': ProductionConfig
    }
    return config_map.get(config_name, DefaultConfig)

def initialize_extensions(app):
    # Initialize your extensions here (e.g., db, migrate)
    pass
