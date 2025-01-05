from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
    strategy="fixed-window",
    enabled=True
)

def init_extensions(app):
    """Initialize all Flask extensions with proper configuration."""
    # Initialize SQLAlchemy with explicit configuration
    db.init_app(app)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
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
