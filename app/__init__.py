from flask import Flask
from flask_migrate import Migrate
from app.extensions import db
from app.routes import register_blueprints

def create_app(config_name='default'):
    from config import get_config
    config = get_config(config_name)
    
    app = Flask(__name__)
    app.config.from_object(config)

    # Initialize extensions
    db.init_app(app)

    # Initialize Flask-Migrate
    migrate = Migrate(app, db)

    # Register blueprints
    register_blueprints(app)  # Removed the with app.app_context() here

    return app  # Just return the app object
