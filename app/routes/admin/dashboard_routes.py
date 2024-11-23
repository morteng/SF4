from flask import Blueprint, render_template
from flask_login import login_required
from app.services.bot_service import get_all_bots
from app.services.organization_service import get_all_organizations
from app.services.stipend_service import get_all_stipends
from app.services.tag_service import get_all_tags
from app.services.user_service import get_all_users

admin_dashboard_bp = Blueprint('admin_dashboard', __name__, url_prefix='/admin')

@admin_dashboard_bp.route('/', methods=['GET'])
@login_required
def index():
    bots = get_all_bots()
    organizations = get_all_organizations()
    stipends = get_all_stipends()
    tags = get_all_tags()
    users = get_all_users()

    return render_template('admin/dashboard.html', 
                           bots=bots, 
                           organizations=organizations, 
                           stipends=stipends, 
                           tags=tags, 
                           users=users)
