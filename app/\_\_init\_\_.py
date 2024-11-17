from flask import Flask
from config import get_config
from app.extensions import db, migrate

def create_app(config_name=None):
    # Load environment variables at the very beginning
    from dotenv import load_dotenv
    load_dotenv()

    # Create the Flask application instance
    app = Flask(__name__)

    # Configure the application
    config = get_config(config_name)
    app.config.from_object(config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints here if needed

    return app
