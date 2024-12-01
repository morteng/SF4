from flask import Blueprint

# Create a parent blueprint for admin routes
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Import sub-modules to register their blueprints
from . import organization_routes, stipend_routes, tag_routes, user_routes, bot_routes

# Register child blueprints with the admin blueprint
admin_bp.register_blueprint(organization_routes.org_bp)
admin_bp.register_blueprint(stipend_routes.stipend_bp)
admin_bp.register_blueprint(tag_routes.tag_bp)
admin_bp.register_blueprint(user_routes.user_bp)
admin_bp.register_blueprint(bot_routes.bot_bp)
