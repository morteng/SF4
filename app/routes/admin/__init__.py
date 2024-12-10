from flask import Blueprint

# Import sub-blueprints
from .bot_routes import admin_bot_bp as bot
from .organization_routes import admin_org_bp as organization
from .stipend_routes import admin_stipend_bp as stipend  
from .tag_routes import admin_tag_bp as tag
from .user_routes import admin_user_bp as user
from .dashboard_routes import admin_dashboard_bp as dashboard

# Register sub-blueprints
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
admin_bp.register_blueprint(bot, url_prefix='/bots')
admin_bp.register_blueprint(organization, url_prefix='/organizations')
admin_bp.register_blueprint(stipend, url_prefix='/stipends')
admin_bp.register_blueprint(tag, url_prefix='/tags')
admin_bp.register_blueprint(user, url_prefix='/users')
admin_bp.register_blueprint(dashboard , url_prefix='/dashboard')

def register_admin_blueprints(app):
    app.register_blueprint(admin_bp)
