from flask import Blueprint
from functools import wraps
from flask_login import current_user
from app.models.notification import Notification
from app.extensions import db

def create_admin_blueprint():
    """Factory function to create a new admin blueprint instance"""
    admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
    
    # Add notification_count decorator
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
    
    # Make the decorator available to routes
    admin_bp.notification_count = notification_count

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

    # Register sub-blueprints only if they haven't been registered
    if 'admin.users' not in app.blueprints:
        admin_bp.register_blueprint(admin_user_bp, url_prefix='/users')
    if 'admin.bots' not in app.blueprints:
        admin_bp.register_blueprint(admin_bot_bp, url_prefix='/bots')
    if 'admin.organizations' not in app.blueprints:
        admin_bp.register_blueprint(admin_org_bp, url_prefix='/organizations')
    if 'admin.stipends' not in app.blueprints:
        admin_bp.register_blueprint(admin_stipend_bp, url_prefix='/stipends')
    if 'admin.tags' not in app.blueprints:
        admin_bp.register_blueprint(admin_tag_bp, url_prefix='/tags')
    if 'admin.dashboard' not in app.blueprints:
        admin_bp.register_blueprint(admin_dashboard_bp, url_prefix='/dashboard')
    
    # Register the main admin blueprint
    if 'admin' not in app.blueprints:
        app.register_blueprint(admin_bp)
