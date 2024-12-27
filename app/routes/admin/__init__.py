from flask import Blueprint
from .user_routes import admin_user_bp
from .bot_routes import admin_bot_bp
from .organization_routes import admin_org_bp
from .stipend_routes import admin_stipend_bp
from .tag_routes import admin_tag_bp
from .dashboard_routes import admin_dashboard_bp

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def register_admin_blueprints(app):
    admin_bp.register_blueprint(admin_user_bp, url_prefix='/users')
    admin_bp.register_blueprint(admin_bot_bp, url_prefix='/bots')
    admin_bp.register_blueprint(admin_org_bp, url_prefix='/organizations')
    admin_bp.register_blueprint(admin_stipend_bp, url_prefix='/stipends')
    admin_bp.register_blueprint(admin_tag_bp, url_prefix='/tags')
    admin_bp.register_blueprint(admin_dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(admin_bp)
