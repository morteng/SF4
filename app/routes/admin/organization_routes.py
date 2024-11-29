from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from app.forms.admin_forms import OrganizationForm
from app.services.organization_service import get_organization_by_id, delete_organization, get_all_organizations, create_organization

org_bp = Blueprint('admin_org', __name__, url_prefix='/admin/organizations')

@org_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = OrganizationForm()
    if form.validate_on_submit():
        new_organization = create_organization(form.data)
        flash('Organization created successfully.', 'success')
        return redirect(url_for('admin_org.index'))
    return render_template('admin/organization/create.html', form=form)

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

@org_bp.route('/', methods=['GET'])
@login_required
def index():
    organizations = get_all_organizations()
    return render_template('admin/organization/index.html', organizations=organizations)
