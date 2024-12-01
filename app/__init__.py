from flask import Flask
from app.config import config_by_name
from app.extensions import db, login_manager
from flask_migrate import Migrate
from app.models.user import User
from app.models import init_models
from app.routes import user_bp, visitor_bp
from app.routes.admin import register_admin_blueprints
from dotenv import load_dotenv
import os

def create_app(config_name='development'):
    load_dotenv()  # Load environment variables from .env file
    
    # Manually set config values
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    # Set other config values as needed

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate = Migrate(app, db)

    # Set up user loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Initialize models
    with app.app_context():
        init_models(app)

    # Register blueprints
    app.register_blueprint(user_bp)
    register_admin_blueprints(app)  # This function handles all admin-related blueprints
    app.register_blueprint(visitor_bp)

    return app
