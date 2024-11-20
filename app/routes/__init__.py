from flask import Blueprint

# Import admin blueprints
from .admin.bot_routes import admin_bot_bp
from .admin.organization_routes import org_bp as admin_org_bp
from .admin.stipend_routes import admin_stipend_bp
from .admin.tag_routes import tag_bp as admin_tag_bp
from .admin.user_routes import user_bp as admin_user_bp

# Create a blueprint for the routes
routes_bp = Blueprint('routes', __name__)

# Register admin blueprints
routes_bp.register_blueprint(admin_bot_bp, url_prefix='/admin/bots')
routes_bp.register_blueprint(admin_org_bp, url_prefix='/admin/organizations')
routes_bp.register_blueprint(admin_stipend_bp, url_prefix='/admin/stipends')
routes_bp.register_blueprint(admin_tag_bp, url_prefix='/admin/tags')
routes_bp.register_blueprint(admin_user_bp, url_prefix='/admin/users')

# Import and register other route modules
from .user_routes import user_bp
from .visitor_routes import visitor_bp

routes_bp.register_blueprint(user_bp, url_prefix='/user')
routes_bp.register_blueprint(visitor_bp)
