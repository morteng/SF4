from flask import Blueprint
from flask_login import login_required  # Import the login_required decorator

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    return "Admin Dashboard"
from flask import Blueprint
from flask_login import login_required

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    return "Admin Dashboard"
from flask import Blueprint
from flask_login import login_required

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    return "Admin Dashboard"
