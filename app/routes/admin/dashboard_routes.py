from flask import Blueprint, render_template

admin_dashboard_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('admin/dashboard.html')
