from app.configs.base_config import BaseConfig, ProductionConfig, TestingConfig
from flask import Flask

def create_app(config_name='development'):
    config = {
        'development': BaseConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }[config_name]()

    app = Flask(__name__)
    app.config.from_object(config)
    # Initialize extensions and other setup
    return app
