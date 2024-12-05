from flask import Blueprint

# Define the main admin blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Import and register sub-blueprints
from .bot_routes import admin_bot_bp
from .organization_routes import admin_org_bp
from .stipend_routes import admin_stipend_bp
from .tag_routes import admin_tag_bp
from .user_routes import admin_user_bp

admin_bp.register_blueprint(admin_bot_bp)
admin_bp.register_blueprint(admin_org_bp)
admin_bp.register_blueprint(admin_stipend_bp)
admin_bp.register_blueprint(admin_tag_bp)
admin_bp.register_blueprint(admin_user_bp)
