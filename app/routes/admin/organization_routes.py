from flask import Blueprint, request, redirect, url_for, render_template, flash
from app.extensions import limiter
from app.services.organization_service import OrganizationService
from app.utils import clean
import logging

# Define rate limits
ORG_RATE_LIMITS = {
    'delete': "5/minute",
    'update': "10/minute"
}

logger = logging.getLogger(__name__)

# Helper functions
def get_organization_by_id(org_id):
    return OrganizationService().get_by_id(org_id)

def delete_organization(organization):
    OrganizationService().delete(organization.id)

def update_organization(organization, data):
    return OrganizationService().update(organization.id, data)

def notification_count(func):
    """Decorator to inject notification count"""
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.controllers.base_route_controller import BaseRouteController
from app.services.organization_service import OrganizationService
from app.forms.admin_forms import OrganizationForm
from app.utils import admin_required, flash_message
from app.models import Organization, AuditLog
from app.constants import FlashMessages, FlashCategory
from app.extensions import db
import logging

admin_org_bp = Blueprint('organization', __name__, url_prefix='/organizations')
org_controller = BaseRouteController(
    OrganizationService(),
    'organization',
    OrganizationForm,
    'admin/organizations'
)

@admin_org_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    return org_controller.create()


@admin_org_bp.route('/<int:id>/delete', methods=['POST'])
@limiter.limit(ORG_RATE_LIMITS['delete'])
@login_required
@admin_required
@notification_count
def delete(id):
    return org_controller.delete(id)
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
@login_required
@admin_required
def index():
    """List organizations with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Use SQLAlchemy's paginate() method directly on the query
    organizations = Organization.query.order_by(Organization.name).paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    return render_template('admin/organizations/index.html',
                         organizations=organizations)

@admin_org_bp.route('/paginate', methods=['GET'])
@login_required
@admin_required
def paginate():
    """Handle pagination requests"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    organizations = Organization.query.order_by(Organization.name).paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    return render_template('admin/organizations/_organizations_table.html', 
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
