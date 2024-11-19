from flask import Blueprint

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Import all necessary blueprints
from .user_routes import user_bp
from .bot_routes import bot_bp  # Ensure this line is correct
