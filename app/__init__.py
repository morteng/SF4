from flask import Flask
from app.configs.base_config import BaseConfig
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Initialize configuration
    app.config = BaseConfig(app.root_path)
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    with app.app_context():
        from app.routes import register_blueprints
        register_blueprints(app)
        
    return app
