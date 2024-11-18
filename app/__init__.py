from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .routes import public_user_routes, public_bot_routes
from .routes.admin import bot_routes, organization_routes, stipend_routes, tag_routes, user_routes

db = SQLAlchemy()

def create_app(config_name='default'):
    app = Flask(__name__)

    # Configuration and initialization...
    # (Assuming you have some configuration setup here)
    app.config.from_object(get_config(config_name))

    # Initialize the database
    db.init_app(app)

    def register_blueprints(app):
        # Register public blueprints
        app.register_blueprint(public_user_routes.bp)
        app.register_blueprint(public_bot_routes.bp)

        # Register admin blueprints
        app.register_blueprint(bot_routes.bot_bp)
        app.register_blueprint(organization_routes.organization_bp)
        app.register_blueprint(stipend_routes.stipend_bp)
        app.register_blueprint(tag_routes.tag_bp)
        app.register_blueprint(user_routes.user_bp)

    register_blueprints(app)

    return app

def get_config(config_name):
    if config_name == 'development':
        from .config import DevelopmentConfig
        return DevelopmentConfig
    elif config_name == 'testing':
        from .config import TestingConfig
        return TestingConfig
    elif config_name == 'production':
        from .config import ProductionConfig
        return ProductionConfig
    else:
        raise ValueError(f"Unknown configuration name: {config_name}")
