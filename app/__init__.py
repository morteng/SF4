import os  # Import the os module here
from flask import Flask

try:
    from flask_limiter import Limiter
except ImportError:
    raise ImportError(
        "Flask-Limiter is required. Please install it using 'pip install Flask-Limiter==3.5.0'"
    )
from app.extensions import db, login_manager, migrate, init_extensions  # Add 'migrate' and 'init_extensions' here
from flask_wtf import CSRFProtect
from dotenv import load_dotenv
from app.utils import init_admin_user  # Import the init_admin_user function

def create_app(config_name='development'):
    app = Flask(__name__)

    # Load environment variables
    load_dotenv()

    from app.config import config_by_name
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Configure CSRF protection
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_SECRET_KEY'] = app.config.get('WTF_CSRF_SECRET_KEY', app.config['SECRET_KEY'])
    csrf = CSRFProtect()
    csrf.init_app(app)

    migrate.init_app(app, db)  # Initialize Flask-Migrate here

    from app.models.user import User  # Import the User model

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))  

    # Initialize rate limiter
    from app.routes.admin.user_routes import init_rate_limiter
    init_rate_limiter(app)

    # Register blueprints
    from app.routes.admin import register_admin_blueprints
    register_admin_blueprints(app)  # For admin routes

    from app.routes import register_blueprints
    register_blueprints(app)        # Register other blueprints

    # Add CSRF error handler
    from flask_wtf.csrf import CSRFError
    from app.constants import FlashMessages

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return FlashMessages.CSRF_INVALID.value, 400

    with app.app_context():
        init_extensions(app)  # Initialize extensions within the application context
        db.create_all()  # Creates all tables if they don't exist
        init_admin_user()  # Initialize the admin user
        
        # Initialize bots
        from app.models.bot import Bot
        if not Bot.query.first():
            bots = [
                Bot(name="TagBot", description="Automatically tags stipends"),
                Bot(name="UpdateBot", description="Updates stale stipend data"),
                Bot(name="ReviewBot", description="Flags suspicious entries")
            ]
            db.session.bulk_save_objects(bots)
            db.session.commit()

    # Initialize rate limiter
    from app.routes.admin.user_routes import init_rate_limiter
    init_rate_limiter(app)

    # Add context processor for notification count
    from app.services.notification_service import get_notification_count
    from flask_login import current_user

    @app.context_processor
    def inject_notification_count():
        if current_user.is_authenticated:
            return {'notification_count': get_notification_count(current_user.id)}
        return {}

    return app
