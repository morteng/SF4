from flask import Blueprint, render_template
from flask_login import current_user
from flask_login import login_required
from app.utils import admin_required


admin_dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@admin_dashboard_bp.route('/')
@login_required
@admin_required
def dashboard():
    from app.models.notification import Notification
    from app.models.audit_log import AuditLog
    from app.models.bot import Bot
    
    # Get recent activity
    recent_activity = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(10).all()
    
    # Get unread notifications
    notification_count = Notification.query.filter_by(
        read_status=False,
        user_id=current_user.id
    ).count()
    
    # Get bot status
    bots = Bot.query.all()
    
    return render_template('admin/dashboard.html',
                         notification_count=notification_count,
                         recent_activity=recent_activity,
                         bots=bots)
