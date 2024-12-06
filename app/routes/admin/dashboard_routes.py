from flask import Blueprint, abort, render_template
from flask_login import login_required, current_user
from app.models.stipend import Stipend
from app.models.tag import Tag
from app.models.organization import Organization
from app.models.user import User
from app.models.bot import Bot

admin_dashboard_bp = Blueprint('admin_dashboard', __name__)

@admin_dashboard_bp.route('/', methods=['GET'])
@login_required
def index():
    """
    Render the admin dashboard page.

    This function checks if the current user is an admin. If not, it aborts with a 403 error.
    It counts the number of stipends, tags, organizations, users, and bots in the database,
    then renders the 'admin/dashboard.html' template with these counts.

    Returns:
        Rendered HTML page for the admin dashboard.
    """
    if not current_user.is_admin:
        abort(403)
    
    stipend_count = Stipend.query.count()
    tag_count = Tag.query.count()
    organization_count = Organization.query.count()
    user_count = User.query.count()
    bot_count = Bot.query.count()
    
    return render_template('admin/dashboard.html', 
                           stipend_count=stipend_count,
                           tag_count=tag_count,
                           organization_count=organization_count,
                           user_count=user_count,
                           bot_count=bot_count)
