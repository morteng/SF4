import json
from flask import Blueprint, redirect, url_for, request, current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.models.notification import Notification, NotificationType
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
    
    # Add CRUD helper methods
    def create_crud_notification(action, object_type, object_id, user_id):
        """Helper to create standardized CRUD notifications"""
        from app.models.notification import Notification
        Notification.create(
            type=f'{object_type.lower()}_{action}',
            message=f'{object_type} {action}d: {object_id}',
            related_object=f'{object_type}/{object_id}',
            user_id=user_id
        )
    
    admin_bp.create_crud_notification = create_crud_notification

    def log_audit(action, object_type, object_id=None, details=None, 
                 details_before=None, details_after=None):
        """Helper function to log admin actions with before/after state"""
        if current_user.is_authenticated:
            try:
                # Serialize complex data
                if details_before and not isinstance(details_before, str):
                    details_before = json.dumps(details_before)
                if details_after and not isinstance(details_after, str):
                    details_after = json.dumps(details_after)
                
                audit_log = AuditLog(
                    user_id=current_user.id,
                    action=action,
                    object_type=object_type,
                    object_id=object_id,
                    details=details,
                    details_before=details_before,
                    details_after=details_after,
                    ip_address=request.remote_addr,
                    http_method=request.method,
                    endpoint=request.endpoint
                )
                db.session.add(audit_log)
                db.session.commit()
                
                # Create notification for significant actions
                if action in ['create', 'update', 'delete']:
                    Notification.create(
                        type=NotificationType.ADMIN_ACTION,
                        message=f"{action.capitalize()} operation on {object_type} {object_id}",
                        related_object=audit_log,
                        user_id=current_user.id
                    )
            except Exception as e:
                current_app.logger.error(f"Failed to create audit log: {str(e)}")
                db.session.rollback()

    # Make audit logging available to routes
    admin_bp.log_audit = log_audit

    
    # Add before_request handler for security checks
    @admin_bp.before_request
    def check_admin_access():
        # Verify CSRF token for POST requests
        if request.method == 'POST' and not validate_csrf(request.form.get('csrf_token')):
            flash_message(FlashMessages.CSRF_ERROR.value, FlashCategory.ERROR.value)
            return redirect(url_for('public.login'))
        
        # Check admin access
        if not current_user.is_authenticated or not current_user.is_admin:
            flash_message(FlashMessages.ADMIN_ACCESS_ERROR.value, FlashCategory.ERROR.value)
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
    def apply_rate_limits(bp):
        @bp.before_request
        def limit_requests():
            # Apply general rate limit
            limiter.limit("100 per hour")(lambda: None)()
            
            # Apply method-specific rate limits
            if request.method == 'POST':
                limiter.limit("10 per minute")(lambda: None)()
            if request.method == 'DELETE':
                limiter.limit("3 per minute")(lambda: None)()
            if request.method == 'POST' and request.path.endswith('/reset_password'):
                limiter.limit("5 per hour", key_func=lambda: f"{get_remote_address()}_reset_password")(lambda: None)()

    # Apply rate limits to all admin blueprints
    for bp in [admin_user_bp, admin_bot_bp, admin_org_bp, 
               admin_stipend_bp, admin_tag_bp]:
        apply_rate_limits(bp)

    # Register sub-blueprints with unique prefixes
    admin_bp.register_blueprint(admin_user_bp, url_prefix='/users')
    admin_bp.register_blueprint(admin_bot_bp, url_prefix='/bots')
    admin_bp.register_blueprint(admin_org_bp, url_prefix='/organizations')
    admin_bp.register_blueprint(admin_stipend_bp, url_prefix='/stipends')
    admin_bp.register_blueprint(admin_tag_bp, url_prefix='/tags')
    admin_bp.register_blueprint(admin_dashboard_bp, url_prefix='/dashboard')

    # Debug logging for route registration
    with app.app_context():
        current_app.logger.debug("Registered admin blueprints:")
        for rule in app.url_map.iter_rules():
            if rule.endpoint.startswith('admin.'):
                current_app.logger.debug(f"Route: {rule}")
    
    # Ensure all routes are properly registered
    with app.app_context():  # Add application context here
        current_app.logger.debug("Registered admin blueprints:")
        for rule in app.url_map.iter_rules():
            if rule.endpoint.startswith('admin.'):
                current_app.logger.debug(f"Route: {rule}")
    
    # Register the main admin blueprint
    app.register_blueprint(admin_bp)
    
    # Mark blueprints as registered
    _admin_blueprints_registered = True
from flask import abort
from functools import wraps
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
