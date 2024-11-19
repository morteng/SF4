from flask import Blueprint

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Import all necessary blueprints
from .user_routes import user_bp
from .bot_routes import bot_routes  # Assuming you have a bot_routes.py file

# Register the user_bp blueprint with the admin_bp
admin_bp.register_blueprint(user_bp)

# Register other blueprints as needed
admin_bp.register_blueprint(bot_routes)
