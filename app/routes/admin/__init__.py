from flask import Blueprint

# Create a parent blueprint for admin routes
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Import and register individual blueprints under the admin_bp
from .auth_routes import auth_bp as admin_auth_bp
from .bot_routes import admin_bot_bp
from .organization_routes import org_bp as admin_org_bp
from .stipend_routes import admin_stipend_bp
from .tag_routes import tag_bp as admin_tag_bp
from .user_routes import user_bp as admin_user_bp

admin_bp.register_blueprint(admin_auth_bp, url_prefix='/auth')
admin_bp.register_blueprint(admin_bot_bp, url_prefix='/bots')
admin_bp.register_blueprint(admin_org_bp, url_prefix='/organizations')
admin_bp.register_blueprint(admin_stipend_bp, url_prefix='/stipends')
admin_bp.register_blueprint(admin_tag_bp, url_prefix='/tags')
admin_bp.register_blueprint(admin_user_bp, url_prefix='/users')

def init_routes(app):
    app.register_blueprint(admin_bp)
