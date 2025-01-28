from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(config_class):
    app = Flask(__name__)
    
    # Initialize configuration
    config = config_class(app.root_path)
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
