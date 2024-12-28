import os  # Import the os module here
import logging
from flask import Flask

# Configure logger
logger = logging.getLogger(__name__)
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

    # Initialize rate limiter with proper storage
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://",
        strategy="fixed-window",  # Explicit strategy
        enabled=not app.config.get('TESTING'),  # Disable in test environment
        storage_options={"check_interval": 1}  # Add storage options
    )
    
    # Initialize with app and force storage creation
    limiter.init_app(app)
    limiter._storage = limiter._create_storage()  # Force storage creation

    # Register blueprints before applying rate limits
    from app.routes.admin import register_admin_blueprints
    from app.routes.admin.user_routes import admin_user_bp
    register_admin_blueprints(app)
    
    # Apply specific limits to admin routes
    limiter.limit("10 per minute")(admin_user_bp)

    # Blueprints will be registered in the app context below

    # Add CSRF error handler
    from flask_wtf.csrf import CSRFError
    from app.constants import FlashMessages


    with app.app_context():
        try:
            # Register blueprints
            from app.routes.admin import register_admin_blueprints
            register_admin_blueprints(app)  # For admin routes

            from app.routes import register_blueprints
            register_blueprints(app)        # Register other blueprints
            
            # Initialize extensions
            init_extensions(app)
            
            # Create database tables
            db.create_all()
            
            # Configure session cleanup with better error handling
            @app.teardown_appcontext
            def shutdown_session(exception=None):
                try:
                    if db.session.is_active:
                        if exception:
                            db.session.rollback()
                            logger.error(f"Session teardown with exception: {exception}")
                            logger.error("Traceback:", exc_info=exception)
                        else:
                            db.session.commit()
                    db.session.remove()
                except Exception as e:
                    logger.error(f"Error during session teardown: {str(e)}")
                    logger.error("Traceback:", exc_info=e)
                    if db.session.is_active:
                        db.session.rollback()
            
            logger.info("Application initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize application: {str(e)}")
            raise RuntimeError(f"Application initialization failed: {str(e)}")
        
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

        # Register rate limited endpoints after blueprints are registered
        if 'admin.bot.run' in app.view_functions:
            limiter.limit("10/hour")(app.view_functions['admin.bot.run'])
        if 'admin.bot.schedule' in app.view_functions:
            limiter.limit("10/hour")(app.view_functions['admin.bot.schedule'])

    # Add context processor for notification count
    from app.services.notification_service import get_notification_count
    from flask_login import current_user

    @app.context_processor
    def inject_notification_count():
        if current_user.is_authenticated:
            return {'notification_count': get_notification_count(current_user.id)}
        return {}

    return app
