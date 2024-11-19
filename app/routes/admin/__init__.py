# app/routes/admin/__init__.py
from flask import Blueprint

admin_bp = Blueprint('admin', __name__)

# Import all admin route modules to register their routes
from .bot_routes import admin_bot_bp
from .organization_routes import admin_org_bp
from .stipend_routes import admin_stipend_bp
from .tag_routes import admin_tag_bp
from .user_routes import admin_user_bp
from .auth_routes import admin_auth_bp

# Register sub-blueprints with the main admin blueprint
admin_bp.register_blueprint(admin_bot_bp, url_prefix='/bots')
admin_bp.register_blueprint(admin_org_bp, url_prefix='/organizations')
admin_bp.register_blueprint(admin_stipend_bp, url_prefix='/stipends')
admin_bp.register_blueprint(admin_tag_bp, url_prefix='/tags')
admin_bp.register_blueprint(admin_user_bp, url_prefix='/users')
admin_bp.register_blueprint(admin_auth_bp)