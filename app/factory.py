from flask import Flask
from app.config import config_by_name
from app.extensions import db, migrate, login_manager, csrf, limiter

def create_app(config_name='development'):
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    
    # Register blueprints
    from app.routes import register_blueprints
    register_blueprints(app)
    
    return app
