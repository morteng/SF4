from dotenv import load_dotenv
import os
from flask import Flask
from .extensions import db

def create_app(config_name):
    load_dotenv()  # Load environment variables from .env file
    app = Flask(__name__)
    
    config = get_config(config_name)
    app.config.from_object(config)  # Set the configuration
    
    # Initialize the database
    init_db(app)
    
    # Register blueprints
    from .routes.admin import admin_bp
    app.register_blueprint(admin_bp)

    return app

def init_db(app):
    with app.app_context():
        db.init_app(app)
        db.create_all()

def run_migrations():
    # Code to run migrations
    pass

def main():
    # Main function code
    pass
