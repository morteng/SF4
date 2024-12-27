import logging
from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import current_user
from bleach import clean

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
from flask_login import login_required
from flask_wtf.csrf import CSRFProtect
from app.constants import FlashMessages, FlashCategory
from app.forms.admin_forms import OrganizationForm
from app.services.organization_service import get_organization_by_id, delete_organization, get_all_organizations, create_organization, update_organization
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.extensions import db
from app.utils import flash_message

admin_org_bp = Blueprint('organization', __name__, url_prefix='/organizations')
csrf = CSRFProtect()

@admin_org_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """
    Create a new organization.
    
    GET: Renders the organization creation form.
    POST: Processes the form submission to create a new organization.
    
    Returns:
        GET: Rendered form template (200 OK)
        POST: Redirect to organization index on success (302 Found)
              Rendered form template with errors on failure (400 Bad Request)
    """
    """Handle organization creation.
    
    GET: Render the organization creation form.
    POST: Validate the form and create the organization.
    
    Returns:
        GET: Rendered form template
        POST: Redirect to organization index or form with errors
    """
    logger.info(f"Organization creation form accessed by user {current_user.username}")
    form = OrganizationForm()
    
    if form.validate_on_submit():
        try:
            # Prepare organization data with cleaned and sanitized inputs
            organization_data = {
                'name': clean(form.name.data.strip(), tags=[], attributes={}),
                'description': clean(form.description.data.strip(), tags=['p', 'br', 'strong', 'em'], attributes={}),
                'homepage_url': clean(form.homepage_url.data.strip(), tags=[], attributes={}) if form.homepage_url.data else None
            }
            
            success, error_message = create_organization(organization_data)
            if success:
                flash_message(FlashMessages.CREATE_ORGANIZATION_SUCCESS, FlashCategory.SUCCESS)
                logger.info(f"Organization '{organization_data['name']}' created successfully by user {current_user.username}")
                return redirect(url_for('admin.organization.index'))
            else:
                logger.error(f"Failed to create organization: {error_message}")
                return handle_organization_error(error_message, form, 'admin/organizations/form.html')
                
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"Integrity error creating organization: {str(e)}", exc_info=True)
            return handle_organization_error(
                FlashMessages.CREATE_ORGANIZATION_DUPLICATE_ERROR,
                form,
                'admin/organizations/form.html'
            )
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error creating organization: {str(e)}", exc_info=True)
            return handle_organization_error(
                FlashMessages.CREATE_ORGANIZATION_DATABASE_ERROR,
                form,
                'admin/organizations/form.html'
            )
        except Exception as e:
            db.session.rollback()
            logger.error(f"Unexpected error creating organization: {str(e)}", exc_info=True)
            return handle_organization_error(
                FlashMessages.GENERIC_ERROR,
                form,
                'admin/organizations/form.html',
                status_code=500
            )
    elif form.errors:
        logger.warning(f"Form validation errors: {form.errors}")
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
    # CSRF token is automatically validated by Flask-WTF
    
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

def handle_organization_error(message, form=None, template=None, status_code=400):
    """Handle organization-related errors consistently"""
    flash_message(message, FlashCategory.ERROR)
    if form and template:
        return render_template(template, form=form), status_code
    return redirect(url_for('admin.organization.index'))

def handle_form_errors(form):
    """Handle form validation errors and flash appropriate messages."""
    for field_name, errors in form.errors.items():
        field_label = form[field_name].label.text
        for error in errors:
            if 'This field is required.' in error:
                message = FLASH_MESSAGES["FORM_FIELD_REQUIRED"].format(field=field_label)
            elif 'Invalid URL format' in error:
                message = FLASH_MESSAGES["FORM_INVALID_URL"].format(field=field_label)
            elif 'Invalid characters' in error:
                message = FLASH_MESSAGES["FORM_INVALID_CHARACTERS"].format(field=field_label)
            else:
                message = f"{field_label}: {error}"
            
            flash_message(message, FLASH_CATEGORY_ERROR)
            logger.warning(f"Form validation error: {message}")
    return render_template('admin/organizations/form.html', form=form), 422
