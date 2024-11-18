from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize the database extension
db = SQLAlchemy()

def create_app(config_name='default'):
    from .config import get_config
    config = get_config(config_name)

    app = Flask(__name__)
    app.config.from_object(config)

    # Initialize extensions
    db.init_app(app)  # Initialize the database with the app

    # Register blueprints
    from .routes import register_blueprints
    register_blueprints(app)

    return app
