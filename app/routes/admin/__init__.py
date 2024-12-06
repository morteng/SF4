from flask import Blueprint
from .auth_routes import auth_bp
from .bot_routes import bot_bp  # Remove 'admin_' prefix from the import
from .organization_routes import org_bp  # Remove 'admin_' prefix from the import
from .stipend_routes import stipend_bp  # Remove 'admin_' prefix from the import
from .tag_routes import tag_bp  # Remove 'admin_' prefix from the import
from .user_routes import user_bp  # Remove 'admin_' prefix from the import

def register_admin_blueprints(app):
    admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
    
    # Register sub-blueprints without the 'admin_' prefix
    admin_bp.register_blueprint(auth_bp)
    admin_bp.register_blueprint(bot_bp)
    admin_bp.register_blueprint(org_bp)
    admin_bp.register_blueprint(stipend_bp)
    admin_bp.register_blueprint(tag_bp)
    admin_bp.register_blueprint(user_bp)
    
    app.register_blueprint(admin_bp)
