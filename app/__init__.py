import os
import logging
from flask import Flask, redirect, url_for, flash
from dotenv import load_dotenv
from sqlalchemy import text
from flask_wtf.csrf import CSRFError
from app.extensions import db, login_manager, limiter
from app.config import config_by_name
from app.services.user_service import create_user, delete_user
from app.models.user import User
from app.routes import register_blueprints
from app.routes.admin import register_admin_blueprints

logger = logging.getLogger(__name__)

def create_app(config_name='development'):
    """Create and configure the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_by_name[config_name])
    app.debug = app.config.get('DEBUG', False)

    _configure_logging(app.debug)
    load_dotenv()

    try:
        # Initialize extensions only once
        if not hasattr(app, 'extensions') or 'sqlalchemy' not in app.extensions:
            init_extensions(app)
            
        _init_database(app)
        _ensure_admin_user(app)
        _register_blueprints(app)
        _add_error_handlers(app)
        _add_context_processors(app)
        logger.info("Application initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}")
        raise RuntimeError(f"Application initialization failed: {str(e)}")

    return app

def _configure_logging(debug):
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def _init_extensions(app):
    """Initialize Flask extensions."""
    # Configure database
    db.init_app(app)
    
    # Configure SQLite-specific settings
    if app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite'):
        engine_options = {
            'poolclass': 'StaticPool',
            'connect_args': {'check_same_thread': False}
        }
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = engine_options
    
    # Configure login manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except Exception as e:
            logger.error(f"Error loading user: {str(e)}")
            return None
            
    # Verify database connection using SQLAlchemy 2.0+ API
    try:
        with app.app_context():
            with db.engine.connect() as connection:
                connection.execute(text('SELECT 1'))
            logger.info("Database connection verified")
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise RuntimeError(f"Database connection failed: {str(e)}")


def _init_database(app):
    """Initialize and verify the database."""
    with app.app_context():
        db.create_all()
        try:
            db.session.execute(text("SELECT 1"))
            logger.info("Database connection successful")
        except Exception as e:
            logger.error(f"Database connection failed: {str(e)}")
            raise RuntimeError(f"Database connection failed: {str(e)}")


def _ensure_admin_user(app):
    """Ensure an admin user exists in the database."""
    admin_username = os.getenv('ADMIN_USERNAME', 'admin')
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
    admin_password = os.getenv('ADMIN_PASSWORD', 'password')

    with app.app_context():
        # Check if admin user already exists
        admin_user = User.query.filter_by(is_admin=True).first()
        if admin_user:
            logger.info(f"Admin user already exists: {admin_user.username}")
            return

        try:
            # Create admin user
            create_user({
                'username': admin_username,
                'email': admin_email,
                'password': admin_password,
                'is_admin': True
            })
            logger.info(f"Created admin user: {admin_username}")
        except Exception as e:
            logger.error(f"Failed to create admin user: {str(e)}")
            # Don't fail the entire app if admin creation fails
            logger.warning("Continuing without admin user creation")


def _register_blueprints(app):
    """Register application blueprints."""
    register_admin_blueprints(app)
    register_blueprints(app)


def _add_error_handlers(app):
    """Add error handlers to the application."""
    @app.errorhandler(CSRFError)
    def handle_csrf_error(error):
        flash("CSRF token missing or invalid", 'error')
        return redirect(url_for('auth.login'))


def _add_context_processors(app):
    """Add context processors to the application."""
    from app.services.notification_service import get_notification_count
    from flask_login import current_user

    @app.context_processor
    def inject_notification_count():
        if current_user.is_authenticated:
            return {'notification_count': get_notification_count(current_user.id)}
        return {}

# Entry point for the application
if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000)
