from flask import Flask
from config import get_config  # Updated import statement
from .extensions import db, migrate

def create_app(config_name=None):
    app = Flask(__name__)
    
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'default')
    
    config = get_config(config_name)
    app.config.from_object(config)

    initialize_extensions(app)
    register_blueprints(app)

    return app

def initialize_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)

def register_blueprints(app):
    from .routes import admin_routes, public_bot_routes, public_user_routes
    app.register_blueprint(admin_routes.bp)
    app.register_blueprint(public_bot_routes.bp)
    app.register_blueprint(public_user_routes.bp)
