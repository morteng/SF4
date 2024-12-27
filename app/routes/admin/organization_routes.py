import logging
from functools import wraps
from flask_login import current_user
from app.models.notification import Notification
from app.services.notification_service import get_notification_count
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user, login_required
from app.utils import admin_required
from bleach import clean
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime
from app.models.organization import Organization
from app.models.audit_log import AuditLog
from app.constants import FlashMessages, FlashCategory
from app.extensions import db, limiter
from app.routes.admin import create_admin_blueprint

# Import notification_count directly
from app.routes.admin import notification_count

# Configure logging
logger = logging.getLogger(__name__)

# Rate limiting configuration
ORG_RATE_LIMITS = {
    'create': "10 per minute",
    'update': "10 per minute", 
    'delete': "3 per minute"
}
from flask_login import login_required
from flask_wtf.csrf import CSRFProtect
from app.constants import FlashMessages, FlashCategory
from app.routes.admin import notification_count
from app.forms.admin_forms import OrganizationForm
from app.services.organization_service import get_organization_by_id, delete_organization, get_all_organizations, create_organization, update_organization
from app.utils import get_unread_notification_count
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.extensions import db
from app.utils import flash_message

admin_org_bp = Blueprint('organization', __name__, url_prefix='/organizations')
csrf = CSRFProtect()

@admin_org_bp.route('/', methods=['GET'])
@login_required
@admin_required
@notification_count
def index():
    """List all organizations"""
    organizations = get_all_organizations()
    return render_template('admin/organizations/index.html',
                         organizations=organizations)

@admin_org_bp.route('/create', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
@login_required
@admin_required
@notification_count
def create():
    """Create a new organization"""
    # Audit log creation
    AuditLog.create(
        user_id=current_user.id,
        action='create_organization',
        object_type='Organization',
        object_id=None,  # Will be set after creation
        details='Attempting to create new organization',
        ip_address=request.remote_addr
    )
    """Create new organization with audit logging and notifications"""
    form = OrganizationForm()
    
    if request.method == 'POST':
        if form.validate():
            try:
                # Prepare organization data
                organization_data = {
                    'name': clean(form.name.data.strip(), tags=[], attributes={}),
                    'description': clean(form.description.data.strip(), tags=['p', 'br', 'strong', 'em'], attributes={}),
                    'homepage_url': clean(form.homepage_url.data.strip(), tags=[], attributes={}) if form.homepage_url.data else None
                }
                
                # Check for duplicate name
                if Organization.query.filter_by(name=organization_data['name']).first():
                    flash_message(FlashMessages.ORGANIZATION_DUPLICATE_NAME, FlashCategory.ERROR)
                    return render_template('admin/organizations/form.html', form=form), 400
                
                # Create organization
                organization = Organization(**organization_data)
                db.session.add(organization)
                db.session.commit()
                
                # Create audit log
                AuditLog.create(
                    user_id=current_user.id,
                    action='create',
                    object_type='Organization',
                    object_id=organization.id,
                    details=f'Created organization {organization.name}',
                    ip_address=request.remote_addr
                )
                
                flash_message(FlashMessages.ORGANIZATION_CREATE_SUCCESS, FlashCategory.SUCCESS)
                return redirect(url_for('admin.organization.index'))
                
            except IntegrityError as e:
                db.session.rollback()
                logger.error(f"Integrity error creating organization: {str(e)}", exc_info=True)
                flash_message(FlashMessages.ORGANIZATION_DUPLICATE_NAME, FlashCategory.ERROR)
                return render_template('admin/organizations/form.html', form=form), 400
                
            except SQLAlchemyError as e:
                db.session.rollback()
                logger.error(f"Database error creating organization: {str(e)}", exc_info=True)
                flash_message(FlashMessages.GENERIC_ERROR, FlashCategory.ERROR)
                return render_template('admin/organizations/form.html', form=form), 500
                
        else:
            logger.warning(f"Form validation errors: {form.errors}")
            flash_message(FlashMessages.ORGANIZATION_INVALID_DATA, FlashCategory.ERROR)
            return handle_form_errors(form)
            
    return render_template('admin/organizations/form.html', form=form)

@admin_org_bp.route('/<int:id>/delete', methods=['POST'])
@limiter.limit(ORG_RATE_LIMITS['delete'])
@login_required
@admin_required
@notification_count
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
            # Create audit log before deletion
            AuditLog.create(
                user_id=current_user.id,
                action='delete_organization',
                object_type='Organization',
                object_id=organization.id,
                details=f'Deleted organization {organization.name}',
                ip_address=request.remote_addr
            )
            
            delete_organization(organization)
            flash_message(FlashMessages.DELETE_ORGANIZATION_SUCCESS, FlashCategory.SUCCESS)
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error deleting organization {id}: {str(e)}")
            flash_message(FlashMessages.DELETE_ORGANIZATION_DATABASE_ERROR, FlashCategory.ERROR)
    else:
        flash_message(FlashMessages.ORGANIZATION_NOT_FOUND, FlashCategory.ERROR)
    
    return redirect(url_for('admin.organization.index'))

@admin_org_bp.route('/', methods=['GET'])
@admin_org_bp.route('/paginate/<int:page>', methods=['GET'])
@login_required
@admin_required
@notification_count
def index(page=1):
    """List organizations with pagination"""
    per_page = 20  # Items per page
    organizations = get_all_organizations().paginate(page=page, per_page=per_page)
    return render_template('admin/organizations/index.html',
                         organizations=organizations)

@admin_org_bp.route('/<int:id>', methods=['GET'])
@login_required
@admin_required
@notification_count
def view(id):
    """View organization details"""
    organization = get_organization_by_id(id)
    if not organization:
        flash_message(FlashMessages.ORGANIZATION_NOT_FOUND, FlashCategory.ERROR)
        return redirect(url_for('admin.organization.index'))
    return render_template('admin/organizations/view.html', organization=organization)

@admin_org_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@limiter.limit(ORG_RATE_LIMITS['update'])
@login_required
@admin_required
@notification_count
def edit(id):
    """Edit an existing organization"""
    organization = get_organization_by_id(id)
    if not organization:
        flash_message(FlashMessages.ORGANIZATION_NOT_FOUND, FlashCategory.ERROR)
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
                    # Create audit log for update
                    AuditLog.create(
                        user_id=current_user.id,
                        action='update_organization',
                        object_type='Organization',
                        object_id=organization.id,
                        details=f'Updated organization {organization.name}',
                        ip_address=request.remote_addr
                    )
                    
                    flash_message(FlashMessages.UPDATE_ORGANIZATION_SUCCESS, FlashCategory.SUCCESS)
                    return redirect(url_for('admin.organization.index'))
                else:
                    flash_message(error_message, FlashCategory.ERROR)
            except SQLAlchemyError as e:
                db.session.rollback()
                flash_message(FlashMessages.UPDATE_ORGANIZATION_DATABASE_ERROR, FlashCategory.ERROR)
        else:
            handle_form_errors(form)

    return render_template('admin/organizations/form.html', form=form, organization=organization)

def handle_organization_error(message, form=None, template=None, status_code=400):
    """Handle organization-related errors consistently"""
    flash(message, category='error')
    if form and template:
        return render_template(template, form=form), status_code
    return redirect(url_for('admin.organization.index'))

def handle_form_errors(form):
    """Handle form validation errors and flash appropriate messages."""
    for field_name, errors in form.errors.items():
        field_label = form[field_name].label.text
        for error in errors:
            if 'This field is required.' in error:
                message = FlashMessages.FORM_FIELD_REQUIRED.format(field=field_label)
            elif 'Invalid URL format' in error:
                message = FlashMessages.FORM_INVALID_URL.format(field=field_label)
            elif 'Invalid characters' in error:
                message = FlashMessages.FORM_INVALID_CHARACTERS.format(field=field_label)
            elif 'Invalid date format' in error:
                message = FlashMessages.FORM_INVALID_DATE_FORMAT.format(field=field_label)
            else:
                message = f"{field_label}: {error}"
            
            flash_message(message, FlashCategory.ERROR)
            logger.warning(f"Form validation error: {message}")
            
            # Audit log the validation error
            AuditLog.create(
                user_id=current_user.id,
                action='validation_error',
                object_type='Organization',
                object_id=None,
                details=f"Validation error in {field_label}: {error}",
                ip_address=request.remote_addr
            )
    return render_template('admin/organizations/form.html', form=form), 422
