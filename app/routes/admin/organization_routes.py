import logging
from flask import Blueprint, render_template, redirect, url_for, request, flash

logger = logging.getLogger(__name__)
from flask_login import login_required
from app.constants import FLASH_MESSAGES, FLASH_CATEGORY_SUCCESS, FLASH_CATEGORY_ERROR
from app.forms.admin_forms import OrganizationForm
from app.services.organization_service import get_organization_by_id, delete_organization, get_all_organizations, create_organization, update_organization
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.extensions import db
from app.utils import flash_message

admin_org_bp = Blueprint('organization', __name__, url_prefix='/organizations')

@admin_org_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """
    Handle the creation of a new organization.
    
    GET: Render the organization creation form.
    POST: Validate the form and create the organization.
    """
    form = OrganizationForm()
    
    if form.validate_on_submit():
        # Clean and validate input data
        organization_data = {
            'name': form.name.data.strip(),
            'description': form.description.data.strip(),
            'homepage_url': form.homepage_url.data.strip() if form.homepage_url.data else None
        }
        
        try:
            success, error_message = create_organization(organization_data)
            if success:
                flash_message(FLASH_MESSAGES["CREATE_ORGANIZATION_SUCCESS"], FLASH_CATEGORY_SUCCESS)
                return redirect(url_for('admin.organization.index'))
            else:
                flash_message(error_message, FLASH_CATEGORY_ERROR)
        except IntegrityError as e:
            db.session.rollback()
            flash_message(FLASH_MESSAGES['CREATE_ORGANIZATION_DUPLICATE_ERROR'], FLASH_CATEGORY_ERROR)
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error creating organization: {str(e)}")
            flash_message(FLASH_MESSAGES['CREATE_ORGANIZATION_DATABASE_ERROR'], FLASH_CATEGORY_ERROR)
    elif form.errors:
        return handle_form_errors(form)
        
    return render_template('admin/organizations/form.html', form=form)

@admin_org_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """
    Handle the deletion of an organization.
    
    Args:
        id (int): The ID of the organization to delete.
        
    Returns:
        Redirect to the organization index page with appropriate flash message.
    """
    # Verify CSRF token
    if not request.form.get('csrf_token'):
        flash_message(FLASH_MESSAGES['CSRF_MISSING'], FLASH_CATEGORY_ERROR)
        return redirect(url_for('admin.organization.index'))
    
    organization = get_organization_by_id(id)
    if organization:
        try:
            delete_organization(organization)
            flash_message(FLASH_MESSAGES["DELETE_ORGANIZATION_SUCCESS"], FLASH_CATEGORY_SUCCESS)
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error deleting organization {id}: {str(e)}")
            flash_message(FLASH_MESSAGES['DELETE_ORGANIZATION_DATABASE_ERROR'], FLASH_CATEGORY_ERROR)
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
            handle_form_errors(form)

    return render_template('admin/organizations/form.html', form=form, organization=organization)

def handle_form_errors(form):
    """Handle form validation errors and flash appropriate messages."""
    for field_name, errors in form.errors.items():
        field_label = form[field_name].label.text
        for error in errors:
            # Preserve field name if already in error message
            if ':' in error:
                message = error
            else:
                # Use more user-friendly messages
                if 'This field is required.' in error:
                    message = f"{field_label} is required."
                elif 'Organization name must contain only letters, numbers, and spaces.' in error:
                    message = f"{field_label} can only contain letters, numbers, and spaces."
                else:
                    message = f"{field_label}: {error}"
            
            flash_message(message, FLASH_CATEGORY_ERROR)
            logger.warning(f"Form validation error: {message}")
    return render_template('admin/organizations/form.html', form=form), 422
