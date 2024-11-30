from flask import Blueprint, abort
from flask_login import login_required, current_user

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_admin:
        # Handle non-admin users, e.g., abort with a 403 Forbidden status
        abort(403)
    return "Admin Dashboard"
