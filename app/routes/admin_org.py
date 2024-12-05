from flask import Blueprint, render_template, request, redirect, url_for
from app.forms.admin_forms import OrganizationForm
from app.services.organization_service import create_organization, get_organization_by_id, get_all_organizations, update_organization

admin_org_bp = Blueprint('org_bp', __name__)

@admin_org_bp.route('/organizations/create', methods=['GET', 'POST'])
def create():
    form = OrganizationForm()
    if form.validate_on_submit():
        organization = create_organization(form.data)
        return redirect(url_for('org_bp.index'))
    return render_template('admin/organization_form.html', form=form)

@admin_org_bp.route('/organizations/delete/<int:id>', methods=['POST'])
def delete(id):
    organization = get_organization_by_id(id)
    if organization:
        # Implement organization deletion logic here
        return redirect(url_for('org_bp.index'))
    return "Organization not found", 404

@admin_org_bp.route('/organizations/', methods=['GET'])
def index():
    organizations = get_all_organizations()
    return render_template('admin/organization_dashboard.html', organizations=organizations)

@admin_org_bp.route('/organizations/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    organization = get_organization_by_id(id)
    if not organization:
        return "Organization not found", 404
    form = OrganizationForm(obj=organization)
    if form.validate_on_submit():
        update_organization(organization, form.data)
        return redirect(url_for('org_bp.index'))
    return render_template('admin/organization_form.html', form=form)
