from flask import Blueprint

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Import the user_bp blueprint
from .user_routes import user_bp

# Register the user_bp blueprint with the admin_bp
admin_bp.register_blueprint(user_bp)
