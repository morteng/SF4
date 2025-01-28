from flask import Flask
from app.configs.base_config import BaseConfig, ProductionConfig
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(env='development'):
    if env == 'development':
        config_class = BaseConfig
    else:
        config_class = ProductionConfig
        
    app = Flask(__name__)
    # Pass app.root_path as a string to BaseConfig
    config = config_class(str(app.root_path))
    app.config = config
    
    # Initialize database
    db.init_app(app)
    
    # Setup paths
    config._setup_paths()
    
    # Register blueprints
    with app.app_context():
        from app.routes import register_blueprints
        register_blueprints(app)
        
    return app
