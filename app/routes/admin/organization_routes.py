from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from app.services.organization_service import get_organization_by_id, delete_organization

org_bp = Blueprint('admin_org', __name__, url_prefix='/organizations')

@org_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    organization = get_organization_by_id(id)
    if organization:
        delete_organization(organization)
        flash(f'Organization {organization.name} deleted.', 'success')
    else:
        flash('Organization not found.', 'danger')
    return redirect(url_for('admin_org.index'))

@org_bp.route('/')
@login_required
def index():
    # Assuming there's a method to get all organizations, let's add it here
    # For now, we'll just render an empty template
    return render_template('admin/organization/index.html')
