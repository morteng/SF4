from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required
from app.forms.admin_forms import OrganizationForm
from app.services.organization_service import get_organization_by_id, delete_organization, get_all_organizations, create_organization, update_organization
from sqlalchemy.exc import SQLAlchemyError

admin_org_bp = Blueprint('organization', __name__, url_prefix='/organizations')

@admin_org_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        form = OrganizationForm(request.form)
        if form.validate_on_submit():
            organization_data = {k: v for k, v in form.data.items() if k != 'submit'}
            try:
                success, error_message = create_organization(organization_data)
                if success:
                    flash('Organization created!', 'success')
                    return redirect(url_for('admin.organization.index'))
                else:
                    flash(error_message, 'danger')
            except SQLAlchemyError as e:
                current_app.db_session.rollback()
                flash(f"Failed to create organization. Error: {e}", 'danger')
    else:
        form = OrganizationForm()
    return render_template('admin/organizations/form.html', form=form)

@admin_org_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    organization = get_organization_by_id(id)
    if organization:
        try:
            delete_organization(organization)
            flash(f'{organization.name} deleted!', 'success')
        except SQLAlchemyError as e:
            current_app.db_session.rollback()
            flash(f'Failed to delete organization. Error: {str(e)}', 'danger')
    else:
        flash('Organization not found.', 'danger')
    return redirect(url_for('admin.organization.index'))

@admin_org_bp.route('/', methods=['GET'])
@login_required
def index():
    organizations = get_all_organizations()
    return render_template('admin/organizations/index.html', organizations=organizations)

@admin_org_bp.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    organization = get_organization_by_id(id)
    if not organization:
        flash('Organization not found.', 'danger')
        return redirect(url_for('admin.organization.index'))

    form = OrganizationForm(original_name=organization.name, obj=organization)
    if request.method == 'POST' and form.validate_on_submit():
        update_data = {k: v for k, v in form.data.items() if k != 'submit'}
        try:
            success, error_message = update_organization(organization, update_data)
            if success:
                flash('Organization updated!', 'success')
                return redirect(url_for('admin.organization.index'))
            else:
                flash(error_message, 'danger')
        except SQLAlchemyError as e:
            current_app.db_session.rollback()
            flash(f'Failed to update organization. Error: {str(e)}', 'danger')

    return render_template('admin/organizations/form.html', form=form, organization=organization)
