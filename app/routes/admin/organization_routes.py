from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.forms.admin_forms import OrganizationForm
from app.services.organization_service import get_organization_by_id, delete_organization, get_all_organizations, create_organization, update_organization

admin_org_bp = Blueprint('organization', __name__, url_prefix='/organizations')

@admin_org_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        form = OrganizationForm(request.form)
        if form.validate_on_submit():
            new_organization = create_organization(form.data)
            flash('Organization created successfully.', 'success')
            return redirect(url_for('admin.organization.index'))
        else:
            flash('Failed to create organization.', 'danger')
    else:
        form = OrganizationForm()
    return render_template('admin/organization/create.html', form=form)

@admin_org_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    organization = get_organization_by_id(id)
    if organization:
        delete_organization(organization)
        flash(f'Organization {organization.name} deleted.', 'success')
    else:
        flash('Organization not found.', 'danger')
    return redirect(url_for('admin.organization.index'))

@admin_org_bp.route('/', methods=['GET'])
@login_required
def index():
    organizations = get_all_organizations()
    return render_template('admin/organization/index.html', organizations=organizations)

@admin_org_bp.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    organization = get_organization_by_id(id)
    if not organization:
        flash('Organization not found.', 'danger')
        return redirect(url_for('admin.organization.index'))
    
    form = OrganizationForm(obj=organization)
    if request.method == 'POST' and form.validate_on_submit():
        update_organization(organization, form.data)
        flash('Organization updated successfully.', 'success')
        return redirect(url_for('admin.organization.index'))
    
    return render_template('admin/organization/update.html', form=form, organization=organization)
