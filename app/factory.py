from flask import Flask
from config import BaseConfig, ProductionConfig, TestingConfig
from config.logging import configure_logging

def create_app(config_name='development'):
    config = {
        'development': BaseConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }[config_name]()

    app = Flask(__name__)
    app.config.from_object(config)
    
    # Configure logging
    configure_logging(app)
    
    # Initialize extensions and other setup
    return app
