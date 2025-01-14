from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect

# Initialize extensions without app context
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])

def init_extensions(app):
    """Initialize all Flask extensions with proper configuration."""
    # Initialize SQLAlchemy
    db.init_app(app)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize rate limiter
    limiter.init_app(app)
    app.extensions['limiter'] = limiter
    
    # Initialize other extensions
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'public.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        try:
            return User.query.get(int(user_id))
        except Exception as e:
            app.logger.error(f"Error loading user: {str(e)}")
            return None
    """Initialize all Flask extensions with proper configuration."""
    # Only initialize extensions if they haven't been initialized yet
    if not hasattr(app, 'extensions') or 'sqlalchemy' not in app.extensions:
        # Initialize SQLAlchemy with explicit configuration
        db.init_app(app)
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Configure database connection handling
        @app.before_request
        def setup_db_connection():
            """Initialize database connection pool and verify connection"""
            if not hasattr(app, 'db_initialized'):
                try:
                    # Test database connection with appropriate pool settings
                    if app.config.get('SQLALCHEMY_DATABASE_URI', '').startswith('sqlite'):
                        # Disable connection pooling for SQLite
                        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
                            'poolclass': 'StaticPool',
                            'connect_args': {'check_same_thread': False}
                        }
                    else:
                        # Use connection pooling for other databases
                        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
                            'pool_size': 10,
                            'max_overflow': 20,
                            'pool_timeout': 30,
                            'pool_recycle': 3600,
                            'pool_pre_ping': True
                        }
                    
                    # Test database connection
                    db.engine.connect()
                    app.logger.info("Database connection established successfully")
                    app.db_initialized = True
                except Exception as e:
                    app.logger.error(f"Failed to connect to database: {str(e)}")
                    raise
                
        @app.teardown_appcontext
        def shutdown_session(exception=None):
            """Clean up database connections after each request"""
            db.session.remove()
            if exception:
                db.session.rollback()
                app.logger.error(f"Database session error: {str(exception)}")
        
        # Initialize Flask-Login with proper settings
        login_manager.init_app(app)
        login_manager.login_view = 'public.login'
        login_manager.login_message_category = 'info'
        
        # Initialize Flask-Migrate with proper configuration
        migrate.init_app(app, db, directory='migrations')
        
        # Initialize CSRF protection with secure settings
        csrf.init_app(app)
        app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 hour
        
        # Initialize rate limiter with proper configuration
        limiter.init_app(app)
        app.config['RATELIMIT_HEADERS_ENABLED'] = True
        
        # Setup user loader with proper error handling
        from app.models.user import User
        
        @login_manager.user_loader
        def load_user(user_id):
            try:
                return db.session.get(User, int(user_id))
            except Exception as e:
                app.logger.error(f"Error loading user: {str(e)}")
                return None
