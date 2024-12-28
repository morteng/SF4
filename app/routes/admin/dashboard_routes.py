from flask import Blueprint, render_template, current_app, request
from flask_login import current_user, login_required
from app.utils import admin_required
from app.extensions import db
from app.models.notification import Notification
from app.models.audit_log import AuditLog
from app.models.bot import Bot
from app.models.user import User

admin_dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@admin_dashboard_bp.route('/')
@login_required
@admin_required
def dashboard():
    # Create audit log for dashboard access
    try:
        audit_log = AuditLog(
            user_id=current_user.id,
            action='view_dashboard',
            details="Accessed admin dashboard",
            ip_address=request.remote_addr,
            http_method=request.method,
            endpoint=request.endpoint
        )
        db.session.add(audit_log)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Error creating audit log: {str(e)}")
        db.session.rollback()

    try:
        # Get recent activity with user information
        recent_activity = db.session.query(AuditLog, User.username)\
            .join(User, AuditLog.user_id == User.id, isouter=True)\
            .order_by(AuditLog.timestamp.desc())\
            .limit(10)\
            .all()
        
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
    except Exception as e:
        current_app.logger.error(f"Error in dashboard route: {str(e)}")
        return render_template('admin/dashboard.html',
                             notification_count=0,
                             recent_activity=[],
                             bots=[])
