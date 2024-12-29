import os
import logging
from flask import Flask
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

def create_app(config_name='development'):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Load environment variables
    load_dotenv()
    
    # Load configuration
    from app.config import config_by_name
    app.config.from_object(config_by_name[config_name])
    
    # Initialize extensions
    from app.extensions import init_extensions
    init_extensions(app)
    
    # Register blueprints
    from app.routes import register_blueprints
    register_blueprints(app)
    
    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG if app.config.get('DEBUG') else logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    
    return app

def init_extensions(app):
    # Initialize extensions only if they haven't been initialized yet
    if not hasattr(app, 'extensions') or 'sqlalchemy' not in app.extensions:
        db.init_app(app)
    # Initialize other extensions
    login_manager.init_app(app)
    migrate.init_app(app, db)
    # Initialize Redis for rate limiting
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    from redis import Redis

    redis = Redis.from_url(app.config.get('REDIS_URL', 'redis://localhost:6379/0'))
    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        storage_uri="redis://localhost:6379/0",  # Use Redis for storage
        default_limits=["200 per day", "50 per hour"]
    )
    # Initialize CSRF protection
    csrf = CSRFProtect(app)
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_SECRET_KEY'] = app.config.get('WTF_CSRF_SECRET_KEY', app.config['SECRET_KEY'])
    app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 hour token validity
    app.config['WTF_CSRF_HEADERS'] = ['X-CSRFToken']
    app.config['WTF_CSRF_SSL_STRICT'] = True

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
            
            # Lazy import to avoid circular dependencies
            from app.common.utils import init_admin_user
            
            # Only run migrations if the env.py file exists
            migrations_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'migrations')
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
