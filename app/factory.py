from flask import Flask
from app.configs.base import BaseConfig

def create_app(config_class=BaseConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions and configure app
    # ... rest of the configuration ...
    
    return app
