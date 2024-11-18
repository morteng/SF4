import os
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
    from .routes.admin import admin_routes
    from .public_bot_routes import bp as public_bot_bp
    from .public_user_routes import bp as public_user_bp

    app.register_blueprint(admin_routes.bp)
    app.register_blueprint(public_bot_bp)
    app.register_blueprint(public_user_bp)

    # Define your routes here
    @public_bot_bp.route('/some-bot-route')
    def some_bot_route():
        return "Bot Route!"
