from flask import Flask
from .extensions import db, migrate
from .config import get_config  # Ensure this import is correct

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Load configuration based on config_name
    config = get_config(config_name)
    if config:
        app.config.from_object(config)
    else:
        raise ValueError(f"Unknown configuration: {config_name}")
    
    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)  # Initialize Migrate with app and db

    # Register blueprints, etc.
    from .routes.admin_routes import admin_bp
    from .routes.bot_routes import bot_bp
    from .routes.user_routes import user_bp
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(bot_bp)

    return app
