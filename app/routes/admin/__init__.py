from flask import Blueprint
from .auth_routes import auth_bp
from .bot_routes import bot_bp
from .organization_routes import organization_bp
from .stipend_routes import stipend_bp
from .tag_routes import tag_bp
from .user_routes import user_bp

def register_admin_blueprints(app):
    admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
    
    # Register sub-blueprints
    admin_bp.register_blueprint(auth_bp)
    admin_bp.register_blueprint(bot_bp)
    admin_bp.register_blueprint(organization_bp)
    admin_bp.register_blueprint(stipend_bp)
    admin_bp.register_blueprint(tag_bp)
    admin_bp.register_blueprint(user_bp)
    
    app.register_blueprint(admin_bp)
