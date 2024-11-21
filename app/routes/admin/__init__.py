from flask import Blueprint

# Create the admin blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Import individual admin route modules
from .bot_routes import admin_bot_bp
from .organization_routes import org_bp as admin_org_bp
from .stipend_routes import admin_stipend_bp
from .tag_routes import tag_bp as admin_tag_bp
from .user_routes import user_bp as admin_user_bp

# Register sub-blueprints under the main admin blueprint
admin_bp.register_blueprint(admin_bot_bp)
admin_bp.register_blueprint(admin_org_bp)
admin_bp.register_blueprint(admin_stipend_bp)
admin_bp.register_blueprint(admin_tag_bp)
admin_bp.register_blueprint(admin_user_bp)
