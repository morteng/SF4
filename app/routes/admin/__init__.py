from flask import Blueprint

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Import and register blueprints from other route files
from .bot_routes import bot_admin_bp  # Renamed to 'bot_admin'
from .stipend_routes import stipend_bp
from .tag_routes import tag_bp
from .organization_routes import organization_bp
from .user_routes import user_bp

# Register the imported blueprints with the main admin blueprint
admin_bp.register_blueprint(bot_admin_bp)  # Renamed to 'bot_admin'
admin_bp.register_blueprint(stipend_bp)
admin_bp.register_blueprint(tag_bp)
admin_bp.register_blueprint(organization_bp)
admin_bp.register_blueprint(user_bp)
