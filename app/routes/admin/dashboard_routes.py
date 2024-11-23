from flask import Blueprint, render_template
from flask_login import login_required

admin_dashboard_bp = Blueprint('admin_dashboard', __name__, url_prefix='/admin')

@admin_dashboard_bp.route('/', methods=['GET'])
@login_required
def index():
    return render_template('admin/dashboard.html')
