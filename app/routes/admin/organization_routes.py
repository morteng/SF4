from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.services.organization_service import get_organization_by_id, update_organization

organization_bp = Blueprint('admin_organization', __name__)

@organization_bp.route('/organizations')
@login_required
def list_organizations():
    # Your code here
    pass

@organization_bp.route('/organizations/<int:organization_id>')
@login_required
def organization_details(organization_id):
    organization = get_organization_by_id(organization_id)
    if not organization:
        flash('Organization not found', 'danger')
        return redirect(url_for('admin_organization.list_organizations'))
    return render_template('admin/organization_details.html', organization=organization)

@organization_bp.route('/organizations/<int:organization_id>/update', methods=['POST'])
@login_required
def update_organization_route(organization_id):
    name = request.form.get('name')
    description = request.form.get('description')
    homepage_url = request.form.get('homepage_url')
    if update_organization(organization_id, name, description, homepage_url):
        flash('Organization updated successfully', 'success')
    else:
        flash('Failed to update organization', 'danger')
    return redirect(url_for('admin_organization.organization_details', organization_id=organization_id))

# Add other routes as needed
