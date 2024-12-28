from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy.orm import scoped_session, sessionmaker

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
csrf_token = generate_csrf  # Use the correct function
migrate = Migrate()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
    strategy="fixed-window"  # Use basic fixed window strategy
)

Session = None
db_session = None

def init_extensions(app):
    global Session, db_session
    with app.app_context():
        Session = sessionmaker(bind=db.engine)
        db_session = scoped_session(Session)
        
        # Initialize rate limiting
        limiter.init_app(app)
        app.extensions['limiter'] = limiter
        # Add exemption for profile edit page
        from app.routes.user_routes import edit_profile
        limiter.exempt(edit_profile)
        
        # Enable CSRF protection
        csrf.init_app(app)
        
        # Initialize audit logging
        from app.models.audit_log import AuditLog
        from flask import request
        from flask_login import current_user
        
        @app.after_request
        def log_request(response):
            if request.endpoint and request.endpoint.startswith('admin.'):
                # Only set object_type if we have a specific object ID
                object_type = None
                object_id = None
                
                # For routes that operate on specific objects (like /admin/stipends/<id>)
                if request.view_args and 'id' in request.view_args:
                    object_type = request.endpoint.split('.')[-1]
                    object_id = request.view_args['id']
                    
                AuditLog.create(
                    user_id=current_user.id if current_user.is_authenticated else 0,
                    action=request.method,
                    object_type=object_type,
                    object_id=object_id,
                    ip_address=request.remote_addr,
                    http_method=request.method,
                    endpoint=request.endpoint,
                    commit=False  # Let the route handler commit
                )
            return response
