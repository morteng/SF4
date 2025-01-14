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
    # Only initialize extensions if they haven't been initialized yet
    if not hasattr(app, 'extensions') or 'sqlalchemy' not in app.extensions:
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
