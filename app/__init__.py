from flask import Flask, Blueprint
from .extensions import db, migrate
from .config import get_config

# Import blueprints
from app.routes.admin import admin_bp
from app.routes.public_user_routes import public_user_bp

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Load configuration using the get_config function
    config_class = get_config(config_name)
    if config_class:
        app.config.from_object(config_class)
    else:
        raise ValueError(f"Unknown configuration name: {config_name}")
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Register blueprints
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(public_user_bp, url_prefix='/')
    
    print("Blueprints registered successfully.")
    
    return app
