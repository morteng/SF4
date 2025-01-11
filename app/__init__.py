import os
import time
import logging
from flask import Flask
from dotenv import load_dotenv
from app.extensions import db, login_manager, migrate, csrf, limiter
from scripts.ensure_admin_user import ensure_admin_user

logger = logging.getLogger(__name__)

def create_app(config_name='development'):
    """Create and configure the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    
    # Load configuration first
    from app.config import config_by_name
    app.config.from_object(config_by_name[config_name])
    
    # Set debug mode based on config
    app.debug = app.config.get('DEBUG', False)
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if app.debug else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        # Load environment variables
        load_dotenv()
        
        # Initialize extensions
        from app.extensions import init_extensions
        init_extensions(app)
        
        # Register blueprints
        from app.routes import register_blueprints
        from app.routes.admin import register_admin_blueprints
        register_admin_blueprints(app)
        register_blueprints(app)
        
        # Ensure admin user exists
        with app.app_context():
            from app.models.user import User
            from app.extensions import db
            from app.services.user_service import delete_user, create_user
            
            # Delete existing admin user if it exists
            admin_user = User.query.filter_by(is_admin=True).first()
            if admin_user:
                logger.info(f"Deleting existing admin user: {admin_user.username}")
                delete_user(admin_user)
            
            # Get admin credentials from .env
            admin_username = os.getenv('ADMIN_USERNAME')
            admin_email = os.getenv('ADMIN_EMAIL')
            admin_password = os.getenv('ADMIN_PASSWORD')
            
            if not all([admin_username, admin_email, admin_password]):
                raise ValueError("Missing admin credentials in .env file")
            
            # Create new admin user
            logger.info("Creating new admin user from .env values")
            create_user({
                'username': admin_username,
                'email': admin_email,
                'password': admin_password,
                'is_admin': True
            }, user_id=0)  # user_id=0 indicates system-initiated action
            
            logger.info(f"Created new admin user: {admin_username}")
                
        logger.info("Application initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}")
        raise RuntimeError(f"Application initialization failed: {str(e)}")
    
    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG if app.config.get('DEBUG') else logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    
    return app


    # Blueprints will be registered in the app context below

    # Add CSRF error handler
    from flask_wtf.csrf import CSRFError
    from app.constants import FlashMessages

    @app.errorhandler(CSRFError)
    def handle_csrf_error(error):
        from flask import flash, redirect, url_for
        flash(FlashMessages.CSRF_ERROR.value, 'error')
        return redirect(url_for('admin.stipend.create'))

    with app.app_context():
        try:
            # Initialize extensions first
            init_extensions(app)
            
            # Lazy import to avoid circular dependencies
            from app.common.utils import init_admin_user
            
            # Only run migrations if the env.py file exists
            migrations_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'migrations')
            env_path = os.path.join(migrations_dir, 'env.py')
            if os.path.exists(env_path):
                from flask_migrate import upgrade
                upgrade()  # Apply migrations only if env.py exists
            
            print("\n=== CHECKING MIGRATIONS ===")
            migrations_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'migrations')
            env_path = os.path.join(migrations_dir, 'env.py')
            print(f"Migrations path: {env_path}")
            print(f"Migrations exist: {os.path.exists(env_path)}")

            # Always check for admin user, regardless of migrations
            print("\n=== CHECKING ADMIN USER ===")
            print("ADMIN_USERNAME:", os.getenv('ADMIN_USERNAME'))
            print("ADMIN_EMAIL:", os.getenv('ADMIN_EMAIL'))
            print("ADMIN_PASSWORD:", os.getenv('ADMIN_PASSWORD'))

            try:
                print("\nAttempting to ensure admin user exists...")
                if not ensure_admin_user():
                    print("\n!!! FAILED TO CREATE ADMIN USER !!!")
                    raise RuntimeError("Admin user initialization failed")
                else:
                    print("\nAdmin user check completed successfully")
            except Exception as e:
                print(f"\n!!! ADMIN USER INITIALIZATION FAILED: {str(e)} !!!")
                raise RuntimeError(f"Admin user initialization failed: {str(e)}")
            
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
def init_extensions(app):
    """Initialize Flask extensions with proper error handling and retry logic."""
    logger = logging.getLogger(__name__)
    max_retries = 3
    retry_delay = 1  # seconds
    
    # Initialize database with retry logic
    for attempt in range(max_retries):
        try:
            db.init_app(app)
            logger.info("Database extension initialized successfully")
            break
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"Failed to initialize database after {max_retries} attempts: {str(e)}")
                raise
            logger.warning(f"Database initialization attempt {attempt + 1} failed, retrying in {retry_delay}s...")
            time.sleep(retry_delay)
    
    # Initialize login manager
    try:
        login_manager.init_app(app)
        login_manager.login_view = 'auth.login'
        logger.info("Login manager initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize login manager: {str(e)}")
        raise

def init_models(app):
    """Initialize database models with proper context."""
    logger = logging.getLogger(__name__)
    
    with app.app_context():
        try:
            from app.models import association_tables
            from app.models.bot import Bot
            from app.models.notification import Notification
            from app.models.organization import Organization
            from app.models.stipend import Stipend
            from app.models.tag import Tag
            from app.models.user import User
            
            # Create database tables if they don't exist
            db.create_all()
            logger.info("Database models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize models: {str(e)}")
            raise

def init_routes(app):
    from app.routes import routes_bp
    app.register_blueprint(routes_bp)
