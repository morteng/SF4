from flask import Blueprint

# Import sub-blueprints
from .bot_routes import admin_bot_bp
from .organization_routes import org_bp
from .stipend_routes import stipend_bp  # Ensure this line is correct
from .tag_routes import tag_bp
from .user_routes import user_bp
from .dashboard_routes import dashboard_bp

# Register sub-blueprints
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
admin_bp.register_blueprint(dashboard_bp)
admin_bp.register_blueprint(admin_bot_bp)  # Ensure this line is correct
admin_bp.register_blueprint(org_bp)  # Corrected import name
admin_bp.register_blueprint(stipend_bp)
admin_bp.register_blueprint(tag_bp)
admin_bp.register_blueprint(user_bp)

def register_admin_blueprints(app):
    app.register_blueprint(admin_bp)
