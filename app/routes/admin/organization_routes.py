from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required
from app.constants import FLASH_MESSAGES, FLASH_CATEGORY_SUCCESS, FLASH_CATEGORY_ERROR
from app.forms.admin_forms import OrganizationForm
from app.services.organization_service import get_organization_by_id, delete_organization, get_all_organizations, create_organization, update_organization
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db
from app.utils import admin_required

admin_org_bp = Blueprint('organization', __name__, url_prefix='/organizations')

@admin_org_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    if request.method == 'POST':
        form = OrganizationForm(request.form)
        if form.validate_on_submit():
            organization_data = {k: v for k, v in form.data.items() if k != 'submit'}
            try:
                success, error_message = create_organization(organization_data)
                if success:
                    flash(FLASH_MESSAGES["CREATE_ORGANIZATION_SUCCESS"], FLASH_CATEGORY_SUCCESS)
                    return redirect(url_for('admin.organization.index'))
                else:
                    flash(error_message, FLASH_CATEGORY_ERROR)
            except SQLAlchemyError as e:
                db.session.rollback()
                flash(f"Failed to create organization. Error: {str(e)}", FLASH_CATEGORY_ERROR)
                return render_template('admin/organizations/form.html', form=form)
    else:
        form = OrganizationForm()
    return render_template('admin/organizations/form.html', form=form)

@admin_org_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(id):
    organization = get_organization_by_id(id)
    if organization:
        try:
            delete_organization(organization)
            flash(FLASH_MESSAGES["DELETE_ORGANIZATION_SUCCESS"], FLASH_CATEGORY_SUCCESS)
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f"Failed to delete organization. Error: {str(e)}", FLASH_CATEGORY_ERROR)
            return render_template('admin/organizations/form.html', form=OrganizationForm())
    else:
        flash(FLASH_MESSAGES["GENERIC_ERROR"], FLASH_CATEGORY_ERROR)  # Use generic error if organization not found
    return redirect(url_for('admin.organization.index'))

@admin_org_bp.route('/', methods=['GET'])
@login_required
@admin_required
def index():
    organizations = get_all_organizations()
    return render_template('admin/organizations/index.html', organizations=organizations)

@admin_org_bp.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
@admin_required
def update(id):
    organization = get_organization_by_id(id)
    if not organization:
        flash(FLASH_MESSAGES["GENERIC_ERROR"], FLASH_CATEGORY_ERROR)  # Use generic error if organization not found
        return redirect(url_for('admin.organization.index'))

    form = OrganizationForm(original_name=organization.name, obj=organization)
    if request.method == 'POST' and form.validate_on_submit():
        update_data = {k: v for k, v in form.data.items() if k != 'submit'}
        try:
            success, error_message = update_organization(organization, update_data)
            if success:
                flash(FLASH_MESSAGES["UPDATE_ORGANIZATION_SUCCESS"], FLASH_CATEGORY_SUCCESS)
                return redirect(url_for('admin.organization.index'))
            else:
                flash(error_message, FLASH_CATEGORY_ERROR)
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f"Failed to update organization. Error: {str(e)}", FLASH_CATEGORY_ERROR)

    return render_template('admin/organizations/form.html', form=form, organization=organization)
