from flask import Flask
from app.configs.base_config import BaseConfig
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(config_class=BaseConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions and configure app
    db.init_app(app)
    config_class().init_app(app)
    
    return app
