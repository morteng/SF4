from flask import Blueprint
from functools import wraps
from flask_login import current_user
from app.models.notification import Notification
from app.extensions import db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

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

def register_admin_blueprints(app):
    from .user_routes import admin_user_bp
    from .bot_routes import admin_bot_bp
    from .organization_routes import admin_org_bp
    from .stipend_routes import admin_stipend_bp
    from .tag_routes import admin_tag_bp
    from .dashboard_routes import admin_dashboard_bp

    # Register blueprints with rate limiting
    admin_bp.register_blueprint(admin_user_bp, url_prefix='/users')
    admin_bp.register_blueprint(admin_bot_bp, url_prefix='/bots')
    admin_bp.register_blueprint(admin_org_bp, url_prefix='/organizations')
    admin_bp.register_blueprint(admin_stipend_bp, url_prefix='/stipends')
    admin_bp.register_blueprint(admin_tag_bp, url_prefix='/tags')
    admin_bp.register_blueprint(admin_dashboard_bp, url_prefix='/dashboard')
    
    # Register the main admin blueprint
    app.register_blueprint(admin_bp)
