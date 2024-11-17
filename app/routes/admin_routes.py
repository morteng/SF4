from flask import Blueprint, jsonify

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('')
def admin_index():
    """
    Returns a greeting message for the admin.
    
    Returns:
        str: A greeting message.
    """
    return 'Hey Admin!', 200
