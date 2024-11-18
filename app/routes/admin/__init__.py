from flask import Blueprint
from .user_routes import admin_user_bp

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
admin_bp.register_blueprint(admin_user_bp)
