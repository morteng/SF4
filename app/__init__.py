from flask import Flask
from config import get_config
from app.extensions import db, migrate
from app.routes.user_routes import user_bp
from app.routes.admin_routes import admin_bp
from app.routes.bot_routes import bot_bp

def create_app(config_name='default'):
    print(f"Creating app with config: {config_name}")
    config = get_config(config_name)
    
    app = Flask(__name__)
    app.config.from_object(config)

    print("Initializing db")
    db.init_app(app)
    print("Initializing migrate")
    migrate.init_app(app, db)

    # Register blueprints
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(bot_bp)

    # Use app context to import models and create tables
    with app.app_context():
        # Import models to ensure they're recognized
        from .models import user, stipend, organization, tag, bot, notification
        
        # Create tables if in development mode
        if config.DEBUG:
            db.create_all()

    return app
