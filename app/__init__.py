import os  # Import the os module here
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

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

    # Initialize CSRF protection
    csrf = CSRFProtect(app)
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_SECRET_KEY'] = app.config.get('WTF_CSRF_SECRET_KEY', app.config['SECRET_KEY'])
    app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 hour token validity
    app.config['WTF_CSRF_HEADERS'] = ['X-CSRFToken']
    app.config['WTF_CSRF_SSL_STRICT'] = True

    migrate.init_app(app, db)  # Initialize Flask-Migrate here

    from app.models.user import User  # Import the User model

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))  

    # Initialize rate limiter
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"]
    )

    # Blueprints will be registered in the app context below

    # Add CSRF error handler
    from flask_wtf.csrf import CSRFError
    from app.constants import FlashMessages


    with app.app_context():
        # Register blueprints
        from app.routes.admin import register_admin_blueprints
        register_admin_blueprints(app)  # For admin routes

        from app.routes import register_blueprints
        register_blueprints(app)        # Register other blueprints
        
        # Initialize extensions
        init_extensions(app)
        
        # Create database tables
        db.create_all()
        
        # Initialize admin user
        init_admin_user()
        
        # Initialize default bots if they don't exist
        from app.models.bot import Bot
        if not Bot.query.first():
            bots = [
                Bot(name="TagBot", description="Automatically tags stipends"),
                Bot(name="UpdateBot", description="Updates stale stipend data"),
                Bot(name="ReviewBot", description="Flags suspicious entries")
            ]
            db.session.bulk_save_objects(bots)
            db.session.commit()
        
        # Initialize bots
        from app.models.bot import Bot
        from app.models.notification import Notification
        from app.models.audit_log import AuditLog
        
        if not Bot.query.first():
            bots = [
                Bot(name="TagBot", description="Automatically tags stipends"),
                Bot(name="UpdateBot", description="Updates stale stipend data"),
                Bot(name="ReviewBot", description="Flags suspicious entries")
            ]
            db.session.bulk_save_objects(bots)
            
            # Create initial notification with system user (0)
            notification = Notification(
                message="System initialized successfully",
                type="system",
                read_status=False,
                user_id=0  # System user
            )
            db.session.add(notification)
            
            # Create audit log for initialization
            AuditLog.create(
                user_id=0,  # System user
                action="system_init",
                details="Application initialized with default bots and admin user",
                object_type="System",
                object_id=0
            )
            
            db.session.commit()

    # Add context processor for notification count
    from app.services.notification_service import get_notification_count
    from flask_login import current_user

    @app.context_processor
    def inject_notification_count():
        if current_user.is_authenticated:
            return {'notification_count': get_notification_count(current_user.id)}
        return {}

    return app
