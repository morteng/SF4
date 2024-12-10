from flask import Blueprint

# Import sub-blueprints
from .bot_routes import admin_bot_bp
from .organization_routes import admin_org_bp
from .stipend_routes import admin_stipend_bp  # Ensure this line is correct
from .tag_routes import admin_tag_bp
from .user_routes import admin_user_bp

# Register sub-blueprints
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
admin_bp.register_blueprint(admin_bot_bp, url_prefix='/bots')
admin_bp.register_blueprint(admin_org_bp, url_prefix='/organizations')
admin_bp.register_blueprint(admin_stipend_bp, url_prefix='/stipends')
admin_bp.register_blueprint(admin_tag_bp, url_prefix='/tags')
admin_bp.register_blueprint(admin_user_bp, url_prefix='/users')

def register_admin_blueprints(app):
    app.register_blueprint(admin_bp)
