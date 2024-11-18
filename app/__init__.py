from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(config_name=None):
    app = Flask(__name__)
    config_class = get_config(config_name or 'default')
    app.config.from_object(config_class)

    initialize_extensions(app)
    register_blueprints(app)

    return app

def get_config(config_name):
    if config_name == 'development':
        from config.development import DevelopmentConfig
        return DevelopmentConfig
    elif config_name == 'testing':
        from config.testing import TestingConfig
        return TestingConfig
    elif config_name == 'production':
        from config.production import ProductionConfig
        return ProductionConfig
    else:
        from config.default import DefaultConfig
        return DefaultConfig

def initialize_extensions(app):
    db.init_app(app)
    # Initialize other extensions here

def register_blueprints(app):
    from app.routes.admin_routes import admin_bp
    from app.routes.public_user_routes import public_user_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(public_user_bp, url_prefix='/user')
