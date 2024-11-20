from flask import Flask
from config import Config
from app.extensions import db

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    init_extensions(app)

    # Register blueprints
    from app.routes.admin import admin_bp
    from app.routes.public_bot_routes import public_bot_bp
    from app.routes.public_user_routes import public_user_bp

    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(public_bot_bp)
    app.register_blueprint(public_user_bp)

    return app

def init_extensions(app):
    db.init_app(app)
