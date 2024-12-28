from flask import Blueprint, redirect, url_for, request
from flask_wtf.csrf import validate_csrf
from functools import wraps
from flask_login import current_user
from app.models.notification import Notification
from app.models.audit_log import AuditLog
from app.extensions import db
from app.utils import flash_message
from app.constants import FlashMessages, FlashCategory

def notification_count(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            count = Notification.query.filter_by(
                user_id=current_user.id,
                read_status=False
            ).count()
            kwargs['notification_count'] = count
        return f(*args, **kwargs)
    return decorated_function

def create_admin_blueprint():
    """Factory function to create a new admin blueprint instance with security and logging"""
    admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

    def log_audit(action, object_type, object_id, details=None):
        """Helper function to log admin actions"""
        if current_user.is_authenticated:
            audit_log = AuditLog(
                user_id=current_user.id,
                action=action,
                object_type=object_type,
                object_id=object_id,
                details=details
            )
            db.session.add(audit_log)
            db.session.commit()
    
    # Add before_request handler for security checks
    @admin_bp.before_request
    def check_admin_access():
        # Verify CSRF token for POST requests
        if request.method == 'POST' and not validate_csrf(request.form.get('csrf_token')):
            flash_message(FlashMessages.CSRF_ERROR.value, FlashCategory.ERROR.value)
            return redirect(url_for('public.login'))
        
        # Check admin access
        if not current_user.is_authenticated or not current_user.is_admin:
            flash_message(FlashMessages.ADMIN_ACCESS_DENIED.value, FlashCategory.ERROR.value)
            return redirect(url_for('public.login'))
    
    # Make the decorator available to routes
    admin_bp.notification_count = notification_count
    
    return admin_bp  # Add this return statement

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

_admin_blueprints_registered = False

def register_admin_blueprints(app):
    global _admin_blueprints_registered
    
    # Only register blueprints once
    if _admin_blueprints_registered:
        return
    
    # Create admin blueprint first
    admin_bp = create_admin_blueprint()
    
    # Initialize rate limiter
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["100 per hour"],
        storage_uri="memory://",
    )
    
    # Import and configure sub-blueprints
    from .user_routes import admin_user_bp
    from .bot_routes import admin_bot_bp
    from .organization_routes import admin_org_bp
    from .stipend_routes import admin_stipend_bp
    from .tag_routes import admin_tag_bp
    from .dashboard_routes import admin_dashboard_bp

    # Configure rate limits for each blueprint
    for bp in [admin_user_bp, admin_bot_bp, admin_org_bp, 
               admin_stipend_bp, admin_tag_bp]:
        bp.before_request(lambda: limiter.limit("100 per hour"))  # Global admin limit
        bp.before_request(lambda: limiter.limit("10 per minute", methods=['POST']))  # Create/Update
        bp.before_request(lambda: limiter.limit("3 per minute", methods=['DELETE']))  # Delete
        bp.before_request(lambda: limiter.limit("5 per hour", methods=['POST'], key_func=lambda: f"{get_remote_address()}_reset_password", 
                          path_func=lambda: request.path.endswith('/reset_password')))  # Password resets

    # Register sub-blueprints with unique prefixes
    admin_bp.register_blueprint(admin_user_bp, url_prefix='/users')
    admin_bp.register_blueprint(admin_bot_bp, url_prefix='/bots')
    admin_bp.register_blueprint(admin_org_bp, url_prefix='/organizations')
    admin_bp.register_blueprint(admin_stipend_bp, url_prefix='/stipends')
    admin_bp.register_blueprint(admin_tag_bp, url_prefix='/tags')
    admin_bp.register_blueprint(admin_dashboard_bp, url_prefix='/dashboard')
    
    # Register the main admin blueprint
    app.register_blueprint(admin_bp)
    
    # Mark blueprints as registered
    _admin_blueprints_registered = True
