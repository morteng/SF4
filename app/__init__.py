from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Load configuration based on config_name
    from .config import get_config
    config = get_config(config_name)
    if config:
        app.config.from_object(config)
    else:
        raise ValueError(f"Unknown configuration: {config_name}")
    
    # Initialize extensions with the app
    db.init_app(app)

    # Register blueprints, etc.
    from .routes import user_routes, admin_routes, bot_routes
    app.register_blueprint(user_routes.bp)
    app.register_blueprint(admin_routes.bp)
    app.register_blueprint(bot_routes.bp)

    return app
