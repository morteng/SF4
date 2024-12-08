from flask import Blueprint, abort, render_template
from flask_login import login_required, current_user
from app.services.stipend_service import get_stipend_count
from app.services.bot_service import get_recent_logs

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_admin:
        # Handle non-admin users, e.g., abort with a 403 Forbidden status
        abort(403)
    
    stipend_count = get_stipend_count()
    bot_logs = get_recent_logs()
    return render_template('admin/_dashboard_data.html', stipend_count=stipend_count, bot_logs=bot_logs)
