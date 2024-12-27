from flask import Blueprint, redirect, url_for
from functools import wraps
from flask_login import current_user
from app.models.notification import Notification
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
        if not current_user.is_authenticated or not current_user.is_admin:
            flash_message(FlashMessages.ADMIN_ACCESS_DENIED.value, FlashCategory.ERROR.value)
            return redirect(url_for('public.login'))
    
    # Make the decorator available to routes
    admin_bp.notification_count = notification_count
    
    return admin_bp  # Add this return statement

def register_admin_blueprints(app):
    # Create a new admin blueprint instance
    admin_bp = create_admin_blueprint()
    
    # Import sub-blueprints
    from .user_routes import admin_user_bp
    from .bot_routes import admin_bot_bp
    from .organization_routes import admin_org_bp
    from .stipend_routes import admin_stipend_bp
    from .tag_routes import admin_tag_bp
    from .dashboard_routes import admin_dashboard_bp

    # Register sub-blueprints with unique prefixes
    admin_bp.register_blueprint(admin_user_bp, url_prefix='/users')
    admin_bp.register_blueprint(admin_bot_bp, url_prefix='/bots')
    admin_bp.register_blueprint(admin_org_bp, url_prefix='/organizations')
    admin_bp.register_blueprint(admin_stipend_bp, url_prefix='/stipends')
    admin_bp.register_blueprint(admin_tag_bp, url_prefix='/tags')
    admin_bp.register_blueprint(admin_dashboard_bp, url_prefix='/dashboard')
    
    # Register the main admin blueprint
    app.register_blueprint(admin_bp)
