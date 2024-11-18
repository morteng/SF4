from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.services.stipend_service import get_stipend_by_id, update_stipend

stipend_bp = Blueprint('admin_stipend', __name__)

@stipend_bp.route('/stipends')
@login_required
def list_stipends():
    # Your code here
    pass

@stipend_bp.route('/stipends/<int:stipend_id>')
@login_required
def stipend_details(stipend_id):
    # Your code here
    pass

# Add other routes as needed
