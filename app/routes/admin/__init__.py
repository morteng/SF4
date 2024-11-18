from flask import Blueprint

# Create a blueprint for the admin routes
admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
def dashboard():
    return "Admin Dashboard"

@admin_bp.route('/stipends')
def stipends():
    return "Stipend Management"
