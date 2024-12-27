from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from app.constants import FLASH_MESSAGES, FLASH_CATEGORY_SUCCESS, FLASH_CATEGORY_ERROR
from app.forms.admin_forms import OrganizationForm
from app.services.organization_service import get_organization_by_id, delete_organization, get_all_organizations, create_organization, update_organization
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db
from app.utils import flash_message

admin_org_bp = Blueprint('organization', __name__, url_prefix='/organizations')

@admin_org_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = OrganizationForm()
    if form.validate_on_submit():
        organization_data = {
            'name': form.name.data,
            'description': form.description.data,
            'homepage_url': form.homepage_url.data
        }
        try:
            success, error_message = create_organization(organization_data)
            if success:
                flash_message(FLASH_MESSAGES["CREATE_ORGANIZATION_SUCCESS"], FLASH_CATEGORY_SUCCESS)
                return redirect(url_for('admin.organization.index'))
            else:
                flash_message(error_message, FLASH_CATEGORY_ERROR)
        except SQLAlchemyError as e:
            db.session.rollback()
            flash_message(FLASH_MESSAGES['CREATE_ORGANIZATION_DATABASE_ERROR'], FLASH_CATEGORY_ERROR)
    else:
        # Handle form validation errors - let the form handle the error message format
        for field_name, errors in form.errors.items():
            for error in errors:
                flash_message(error, FLASH_CATEGORY_ERROR)
        return render_template('admin/organizations/form.html', form=form), 422
    return render_template('admin/organizations/form.html', form=form)

@admin_org_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    organization = get_organization_by_id(id)
    if organization:
        try:
            delete_organization(organization)
            flash_message(FLASH_MESSAGES["DELETE_ORGANIZATION_SUCCESS"], FLASH_CATEGORY_SUCCESS)
        except SQLAlchemyError as e:
            db.session.rollback()
            flash_message(FLASH_MESSAGES['DELETE_ORGANIZATION_DATABASE_ERROR'], FLASH_CATEGORY_ERROR)  # Directly use the constant
            return redirect(url_for('admin.organization.index'))
    else:
        flash_message(FLASH_MESSAGES["ORGANIZATION_NOT_FOUND"], FLASH_CATEGORY_ERROR)
    return redirect(url_for('admin.organization.index'))

@admin_org_bp.route('/', methods=['GET'])
@login_required
def index():
    organizations = get_all_organizations()
    return render_template('admin/organizations/index.html', organizations=organizations)

@admin_org_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    organization = get_organization_by_id(id)
    if not organization:
        flash_message(FLASH_MESSAGES["ORGANIZATION_NOT_FOUND"], FLASH_CATEGORY_ERROR)
        return redirect(url_for('admin.organization.index'))

    form = OrganizationForm(obj=organization)
    if request.method == 'POST':
        if form.validate_on_submit():
            update_data = {
                'name': form.name.data,
                'description': form.description.data,
                'homepage_url': form.homepage_url.data
            }
            try:
                success, error_message = update_organization(organization, update_data)
                if success:
                    flash_message(FLASH_MESSAGES["UPDATE_ORGANIZATION_SUCCESS"], FLASH_CATEGORY_SUCCESS)
                    return redirect(url_for('admin.organization.index'))
                else:
                    flash_message(error_message, FLASH_CATEGORY_ERROR)
            except SQLAlchemyError as e:
                db.session.rollback()
                flash_message(FLASH_MESSAGES['UPDATE_ORGANIZATION_DATABASE_ERROR'], FLASH_CATEGORY_ERROR)
        else:
            # Handle form validation errors
            for field_name, errors in form.errors.items():
                field_label = 'Org Name' if field_name == 'name' else form[field_name].label.text
                for error in errors:
                    if 'This field is required.' in error:
                        flash_message(f"{field_label}: This field is required.", FLASH_CATEGORY_ERROR)
                    else:
                        flash_message(f"{field_label}: {error}", FLASH_CATEGORY_ERROR)

    return render_template('admin/organizations/form.html', form=form, organization=organization)
