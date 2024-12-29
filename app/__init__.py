import os
import logging
from flask import Flask

logger = logging.getLogger(__name__)

def check_dependencies():
    required_deps = ["flask", "flask_login", "werkzeug", "flask_sqlalchemy", "flask_migrate"]
    missing_deps = []
    for dep in required_deps:
        try:
            __import__(dep)
        except ImportError:
            missing_deps.append(dep)
    if missing_deps:
        raise RuntimeError(f"Missing dependencies: {', '.join(missing_deps)}. Run 'pip install -r requirements.txt' to install them.")
def get_limiter():
    """Lazy import for Limiter to avoid circular imports"""
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    return Limiter, get_remote_address

try:
    Limiter, get_remote_address = get_limiter()
except ImportError:
    raise ImportError(
        "Flask-Limiter is required. Please install it using 'pip install Flask-Limiter==3.5.0'"
    )
from app.extensions import db, login_manager, migrate, init_extensions  # Add 'migrate' and 'init_extensions' here
from flask_wtf import CSRFProtect
from dotenv import load_dotenv
# Lazy import to avoid circular dependencies

def create_app(config_name='development'):
    app = Flask(__name__)
    
    try:
        # Check dependencies before proceeding
        check_dependencies()

        # Set up migrations directory in root project directory
        basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # Go up one level
        migrations_dir = os.path.join(basedir, 'migrations')

        # Ensure migrations directory exists
        if not os.path.exists(migrations_dir):
            os.makedirs(migrations_dir)
            logger.info(f"Created migrations directory at {migrations_dir}")

        # Configure SQLAlchemy database URI
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', f'sqlite:///{os.path.join(basedir, "app.db")}')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        # Load environment variables
        try:
            load_dotenv()
        except Exception as e:
            logger.error(f"Failed to load environment variables: {str(e)}")
            raise RuntimeError(f"Environment variable loading failed: {str(e)}")

        from app.config import config_by_name
        app.config.from_object(config_by_name[config_name])
    except Exception as e:
        logger.error(f"Failed to initialize application configuration: {str(e)}")
        raise RuntimeError(f"Application configuration failed: {str(e)}")

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

    # Initialize rate limiter from extensions
    from app.extensions import limiter
    limiter.init_app(app)
    
    # Ensure limiter is fully disabled in test environment
    if app.config.get('TESTING'):
        limiter.enabled = False
        app.config['RATELIMIT_ENABLED'] = False
    
    # Ensure limiter is fully disabled in test environment
    if app.config.get('TESTING'):
        limiter.enabled = False
        app.config['RATELIMIT_ENABLED'] = False

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
            # Initialize extensions first
            init_extensions(app)
            
            # Only run migrations if the env.py file exists
            env_path = os.path.join(migrations_dir, 'env.py')
            if os.path.exists(env_path):
                from flask_migrate import upgrade
                upgrade()  # Apply migrations only if env.py exists
            
            # Only initialize admin user if not in test mode and after migrations
            if not app.config.get('TESTING') and os.path.exists(env_path):
                try:
                    init_admin_user()  # Now the tables exist
                except Exception as e:
                    logger.warning(f"Admin user initialization failed: {str(e)}")
                    logger.warning("This is normal during initial setup. Run 'flask db upgrade' to create the database tables.")
            
            # Register blueprints
            from app.routes.admin import register_admin_blueprints
            register_admin_blueprints(app)  # For admin routes

            from app.routes import register_blueprints
            register_blueprints(app)        # Register other blueprints
            
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
        
        
            # Initialize bots only after migrations are complete
            if os.path.exists(env_path):
                try:
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
                except Exception as e:
                    logger.warning(f"Bot initialization failed: {str(e)}")
                    logger.warning("This is normal during initial setup. Run 'flask db upgrade' to create the database tables.")

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
