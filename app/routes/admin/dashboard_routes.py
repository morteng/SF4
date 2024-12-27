from flask import Blueprint, render_template
from flask_login import login_required
from app.utils import admin_required


admin_dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@admin_dashboard_bp.route('/')
@login_required
@admin_required
def dashboard():
    from app.models.notification import Notification
    notification_count = Notification.query.filter_by(read_status=False).count()
    return render_template('admin/dashboard.html', notification_count=notification_count)
