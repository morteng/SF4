from flask import Flask
from config import Config, DevelopmentConfig, TestingConfig, ProductionConfig
from app.extensions import db
import os
from dotenv import load_dotenv

def create_app(config_name=None):
    # Load environment variables from .env file
    load_dotenv()

    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')

    # Create and configure the app
    app = Flask(__name__)

    # Configure the app based on the selected configuration class
    if config_name == 'development':
        app.config.from_object(DevelopmentConfig)
    elif config_name == 'testing':
        app.config.from_object(TestingConfig)
    elif config_name == 'production':
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    from app.routes.admin.bot_routes import admin_bot_bp
    from app.routes.admin.organization_routes import org_bp
    from app.routes.admin.tag_routes import tag_bp
    from app.routes.admin.user_routes import admin_user_bp
    from app.routes.admin.stipend_routes import stipend_bp

    app.register_blueprint(admin_bot_bp)
    app.register_blueprint(org_bp)
    app.register_blueprint(tag_bp)
    app.register_blueprint(admin_user_bp)
    app.register_blueprint(stipend_bp)

    return app

def init_db():
    """Initialize the database."""
    from app.models.user import User
    from app.models.bot import Bot
    from app.models.organization import Organization
    from app.models.tag import Tag
    from app.models.stipend import Stipend
    db.create_all()

def run_migrations():
    """Run database migrations."""
    # Placeholder for running migrations using Alembic or similar tool
    pass

def run_tests():
    """Run tests using pytest."""
    import pytest
    pytest.main(['-v', 'tests/'])

def init_admin_user():
    """Initialize admin user if it doesn't exist."""
    from app.utils import init_admin_user as utils_init_admin_user
    return utils_init_admin_user()
