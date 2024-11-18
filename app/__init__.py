import os
from flask import Flask
from config import get_config

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'default')
    
    config = get_config(config_name)
    
    app = Flask(__name__)
    app.config.from_object(config)

    # Initialize extensions
    from .extensions import db, migrate  # Ensure you have the migrate extension defined
    db.init_app(app)
    migrate.init_app(app, db)

    # Register routes
    from .routes import public_user_routes, admin_routes, public_bot_routes  # Add public_bot_routes here
    app.register_blueprint(public_user_routes.bp)
    app.register_blueprint(admin_routes.bp)
    app.register_blueprint(public_bot_routes.public_bot_bp)  # Register the bot blueprint

    return app
