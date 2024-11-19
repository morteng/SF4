from flask import Blueprint

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Import and register all necessary blueprints
from .user_routes import user_bp
from .bot_routes import bot_bp

admin_bp.register_blueprint(user_bp)
admin_bp.register_blueprint(bot_bp)
