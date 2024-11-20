from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models.stipend import Stipend
from app.forms.admin_forms import StipendForm  # Corrected import path
from app.services.stipend_service import get_stipend_by_id, delete_stipend

admin_stipend_bp = Blueprint('admin_stipend', __name__)

@admin_stipend_bp.route('/list')
@login_required
def list_stipends():
    # Logic to list stipends for admin
    pass

@admin_stipend_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_stipend():
    # Logic to create a new stipend by admin
    pass

@admin_stipend_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_stipend(id):
    # Logic to edit an existing stipend by admin
    pass

@admin_stipend_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_stipend(id):
    stipend = get_stipend_by_id(id)
    if stipend is None:
        flash('Stipend not found', 'danger')
        return redirect(url_for('admin_stipend.list_stipends'))
    
    delete_stipend(stipend)
    flash('Stipend deleted successfully', 'success')
    return redirect(url_for('admin_stipend.list_stipends'))
