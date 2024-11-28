from flask import Flask
from .config import config_by_name
from .extensions import db, login_manager
from .models import *  # Import models here to ensure db is initialized first

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    from .routes import blueprint
    app.register_blueprint(blueprint)

    return app
