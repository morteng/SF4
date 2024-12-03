from dotenv import load_dotenv
import os
from flask import Flask
from flask_login import LoginManager
from app.extensions import db
from app.config import config_by_name
# Importing admin blueprints
from app.routes.admin import admin_bp
from app.routes.user_routes import user_bp
from app.routes.visitor_routes import visitor_bp

# Importing all models to ensure they are registered with SQLAlchemy
from app.models.user import User
from app.models.bot import Bot
from app.models.organization import Organization
from app.models.stipend import Stipend
from app.models.notification import Notification
from app.models.tag import Tag
from app.models.association_tables import user_organization, bot_tag

def create_app(config_name='development'):
    # Load environment variables from .env file
    load_dotenv()
    
    app = Flask(__name__, instance_relative_config=True)
    print(f"DATABASE_URL from env: {os.environ.get('DATABASE_URL')}")
    app.config.from_object(config_by_name[config_name])

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
        print(f"Instance folder created at: {app.instance_path}")
    except OSError:
        print(f"Instance folder already exists at: {app.instance_path}")

    print(f"Instance path: {app.instance_path}")
    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"Database file path: {os.path.join(app.instance_path, 'site.db')}")
    print(f"Loaded SECRET_KEY: {os.environ.get('SECRET_KEY')}")
    print(f"Loaded DATABASE_URL: {os.environ.get('DATABASE_URL')}")
    print(f"Loaded FLASK_CONFIG: {os.environ.get('FLASK_CONFIG')}")

    db.init_app(app)

    with app.app_context():
        if config_name == 'testing':
            db.create_all()  # Create tables for the in-memory SQLite database
        else:
            db.create_all()  # Ensure tables are created for other configurations

    # Initialize LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Registering admin blueprint
    app.register_blueprint(admin_bp)

    # Registering user and visitor blueprints
    app.register_blueprint(user_bp)
    app.register_blueprint(visitor_bp)

    return app
