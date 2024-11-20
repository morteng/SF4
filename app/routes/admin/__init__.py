from flask import Blueprint

# Create a blueprint for admin routes
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Import and register other blueprints or routes here
from .auth_routes import auth_bp
from .bot_routes import admin_bot_bp
from .organization_routes import org_bp
from .tag_routes import tag_bp
from .user_routes import user_bp
from .stipend_routes import admin_stipend_bp

admin_bp.register_blueprint(auth_bp)
admin_bp.register_blueprint(admin_bot_bp, url_prefix='/bots')
admin_bp.register_blueprint(org_bp, url_prefix='/organizations')
admin_bp.register_blueprint(tag_bp, url_prefix='/tags')
admin_bp.register_blueprint(user_bp, url_prefix='/users')
admin_bp.register_blueprint(admin_stipend_bp, url_prefix='/stipends')
