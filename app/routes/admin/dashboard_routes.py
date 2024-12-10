from flask import Blueprint, render_template
from flask_login import login_required

admin_dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@admin_dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('admin/dashboard.html')

