# app/__init__.py

import os  # Import the os module here
from flask import Flask
from app.extensions import db, login_manager, migrate  # Add 'migrate' here
from flask_wtf import CSRFProtect
from dotenv import load_dotenv

def create_app(config_name='development'):
    app = Flask(__name__)

    # Load environment variables
    load_dotenv()

    if config_name == 'testing':
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///:memory:')
        app.config['WTF_CSRF_ENABLED'] = False  # Keep this as False for testing
        app.config['SERVER_NAME'] = 'localhost'
        app.config['APPLICATION_ROOT'] = '/'
        app.config['PREFERRED_URL_SCHEME'] = 'http'
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'test_secret_key')  # Add this line
        app.config['TEMPLATES_AUTO_RELOAD'] = True  # Enable template auto-reload for testing
    else:
        from app.config import config_by_name
        app.config.from_object(config_by_name[config_name])

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    csrf = CSRFProtect()
    csrf.init_app(app)  # Initialize CSRF protection

    migrate.init_app(app, db)  # Initialize Flask-Migrate here

    from app.models.user import User  # Import the User model

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))  

    # Register blueprints
    from app.routes.admin import register_admin_blueprints
    register_admin_blueprints(app)  # For admin routes

    from app.routes import register_blueprints
    register_blueprints(app)        # Register other blueprints

    return app
