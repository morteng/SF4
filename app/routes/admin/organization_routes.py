from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.services.organization_service import get_organization_by_id, update_organization, create_organization, delete_organization, list_all_organizations

organization_bp = Blueprint('admin_organization', __name__)

@organization_bp.route('/organizations', methods=['GET'])
@login_required
def list_organizations():
    organizations = list_all_organizations()
    return render_template('admin/organization_list.html', organizations=organizations)

@organization_bp.route('/organization/<int:organization_id>', methods=['GET'])
@login_required
def view_organization(organization_id):
    organization = get_organization_by_id(organization_id)
    if organization is None:
        flash('Organization not found.', 'danger')
        return redirect(url_for('admin_organization.list_organizations'))
    return render_template('admin/organization_detail.html', organization=organization)

@organization_bp.route('/organization/create', methods=['GET', 'POST'])
@login_required
def create_organization_route():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        homepage_url = request.form.get('homepage_url')
        organization = create_organization(name, description, homepage_url)
        flash(f'Organization {organization.name} created successfully.', 'success')
        return redirect(url_for('admin_organization.list_organizations'))
    return render_template('admin/organization_form.html')

@organization_bp.route('/organization/<int:organization_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_organization_route(organization_id):
    organization = get_organization_by_id(organization_id)
    if organization is None:
        flash('Organization not found.', 'danger')
        return redirect(url_for('admin_organization.list_organizations'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        homepage_url = request.form.get('homepage_url')
        update_organization(organization_id, name, description, homepage_url)
        flash(f'Organization {organization.name} updated successfully.', 'success')
        return redirect(url_for('admin_organization.view_organization', organization_id=organization.id))
    
    return render_template('admin/organization_form.html', organization=organization)

@organization_bp.route('/organization/<int:organization_id>/delete', methods=['POST'])
@login_required
def delete_organization_route(organization_id):
    organization = get_organization_by_id(organization_id)
    if organization is None:
        flash('Organization not found.', 'danger')
        return redirect(url_for('admin_organization.list_organizations'))
    
    delete_organization(organization_id)
    flash(f'Organization {organization.name} deleted successfully.', 'success')
    return redirect(url_for('admin_organization.list_organizations'))

print("Admin organization blueprint initialized successfully.")
