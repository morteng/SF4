from flask_login import LoginManager
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect

login_manager = LoginManager()
migrate = Migrate(compare_type=True)
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])

def init_extensions(app):
    """Initialize all Flask extensions with proper configuration."""
    # Initialize security components first
    login_manager.init_app(app)
    limiter.init_app(app)
    limiter.storage_uri = "memory://"  # Required for Windows compatibility
    csrf.init_app(app)
    app.extensions['limiter'] = limiter
    
    # Initialize database with SQLite batch mode
    from app.database import db
    db.init_app(app)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    migrate.init_app(app, db, render_as_batch=True, compare_type=True)
    
    # Configure admin rate limits
    from app.routes.admin import admin_bp
    limiter.limit("100/hour")(admin_bp)
    
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
