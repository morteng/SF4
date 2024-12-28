from datetime import datetime
import logging
import pytz
from app.models.notification import NotificationType
from sqlalchemy.exc import IntegrityError
from wtforms.validators import ValidationError

from flask import Blueprint, render_template, redirect, url_for, request, current_app, render_template_string, flash
from app.services.notification_service import create_crud_notification
from app.models.audit_log import AuditLog
from app.models.notification import Notification
from app.services.notification_service import get_notification_count
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per hour", "10 per minute"]
)
from flask_login import current_user
from app.models.audit_log import AuditLog
from app.utils import format_error_message
from jinja2 import TemplateNotFound
from flask_login import login_required

from app.constants import FlashCategory, FlashMessages
from app.forms.admin_forms import StipendForm, OrganizationForm
from app.models.stipend import Stipend
from app.models.organization import Organization
from app.models.tag import Tag
from app.services.organization_service import get_organization_by_id
from app.services.stipend_service import (
    get_stipend_by_id,
    delete_stipend,
    get_all_stipends,
    create_stipend,
    update_stipend
)
from app.extensions import db
from app.utils import admin_required, flash_message, log_audit, create_notification

admin_stipend_bp = Blueprint('stipend', __name__, url_prefix='/stipends')


@admin_stipend_bp.route('/create', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
@login_required
@admin_required
def create():
    """Enhanced stipend creation with better error handling and logging"""
    try:
        form = StipendForm()
        is_htmx = request.headers.get('HX-Request')
        
        # Initialize form choices
        organizations = Organization.query.order_by(Organization.name).all()
        tags = Tag.query.order_by(Tag.name).all()
        form.organization_id.choices = [(org.id, org.name) for org in organizations]
        form.tags.choices = [(tag.id, tag.name) for tag in tags]
        
        if form.validate_on_submit():
            # Prepare stipend data
            stipend_data = {
                'name': form.name.data,
                'summary': form.summary.data,
                'description': form.description.data,
                'homepage_url': form.homepage_url.data,
                'application_procedure': form.application_procedure.data,
                'eligibility_criteria': form.eligibility_criteria.data,
                'application_deadline': form.application_deadline.data,
                'organization_id': form.organization_id.data,
                'open_for_applications': form.open_for_applications.data,
                'tags': form.tags.data  # Will be handled in model __init__
            }
    """Create new stipend with audit logging and notifications"""
    form = StipendForm()
    is_htmx = request.headers.get('HX-Request')
    
    # Initialize form choices
    organizations = Organization.query.order_by(Organization.name).all()
    tags = Tag.query.order_by(Tag.name).all()
    form.organization_id.choices = [(org.id, org.name) for org in organizations]
    form.tags.choices = [(tag.id, tag.name) for tag in tags]
    
    if form.validate_on_submit():
        try:
            # Prepare stipend data
            stipend_data = {
                'name': form.name.data,
                'summary': form.summary.data,
                'description': form.description.data,
                'homepage_url': form.homepage_url.data,
                'application_procedure': form.application_procedure.data,
                'eligibility_criteria': form.eligibility_criteria.data,
                'application_deadline': form.application_deadline.data,
                'organization_id': form.organization_id.data,
                'open_for_applications': form.open_for_applications.data,
                'tags': [Tag.query.get(tag_id) for tag_id in form.tags.data]
            }
            
            # Create stipend
            stipend = Stipend.create(stipend_data)
            
            # Create audit log
            log_audit(
                user_id=current_user.id,
                action='create_stipend',
                object_type='Stipend',
                object_id=stipend.id,
                after=stipend.to_dict()
            )
            
            # Create notification
            create_notification(
                type='stipend_created',
                message=f'New stipend created: {stipend.name}',
                related_object=stipend,
                user_id=current_user.id
            )
            
            flash_message(FlashMessages.STIPEND_CREATE_SUCCESS, FlashCategory.SUCCESS)
            
            if is_htmx:
                return render_template('admin/stipends/_stipend_row.html', stipend=stipend), 200, {
                    'HX-Trigger': 'stipendCreated'
                }
            return redirect(url_for('admin.stipend.index'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating stipend: {str(e)}")
            flash_message(f"{FlashMessages.STIPEND_CREATE_ERROR}: {str(e)}", FlashCategory.ERROR)
            if is_htmx:
                return render_template('admin/stipends/_form.html', form=form), 400
    
    return render_template('admin/stipends/create.html', form=form)
    """Create new stipend with HTMX support and audit logging"""
    form = StipendForm()
    is_htmx = request.headers.get('HX-Request')
    
    # Initialize form choices
    organizations = Organization.query.order_by(Organization.name).all()
    tags = Tag.query.order_by(Tag.name).all()
    form.organization_id.choices = [(org.id, org.name) for org in organizations]
    form.tags.choices = [(tag.id, tag.name) for tag in tags]
    
    if form.validate_on_submit():
        try:
            # Create stipend
            stipend = Stipend(
                name=form.name.data,
                summary=form.summary.data,
                description=form.description.data,
                homepage_url=form.homepage_url.data,
                application_procedure=form.application_procedure.data,
                eligibility_criteria=form.eligibility_criteria.data,
                application_deadline=form.application_deadline.data,
                organization_id=form.organization_id.data,
                open_for_applications=form.open_for_applications.data
            )
            
            # Add tags
            for tag_id in form.tags.data:
                tag = Tag.query.get(tag_id)
                if tag:
                    stipend.tags.append(tag)
            
            db.session.add(stipend)
            db.session.commit()

            # Create audit log
            audit_log = AuditLog(
                user_id=current_user.id,
                action='create_stipend',
                object_type='Stipend',
                object_id=stipend.id,
                ip_address=request.remote_addr,
                http_method=request.method,
                endpoint=request.endpoint,
                details=f"Created stipend: {stipend.name}"
            )
            db.session.add(audit_log)
            db.session.commit()
            
            # Create notification
            Notification.create(
                type='STIPEND_CREATED',
                message=f'New stipend created: {stipend.name}',
                related_object=stipend
            )
            
            flash_message(FlashMessages.STIPEND_CREATE_SUCCESS, FlashCategory.SUCCESS)
            
            if is_htmx:
                return render_template('admin/stipends/_stipend_row.html', stipend=stipend), 200, {
                    'HX-Trigger': 'stipendCreated'
                }
            return redirect(url_for('admin.stipend.index'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating stipend: {str(e)}")
            flash_message(f"{FlashMessages.STIPEND_CREATE_ERROR}: {str(e)}", FlashCategory.ERROR)
            if is_htmx:
                return render_template('admin/stipends/_form.html', form=form), 400
    
    return render_template('admin/stipends/create.html', form=form)
    """Create new stipend with HTMX support and audit logging"""
    form = StipendForm()
    is_htmx = request.headers.get('HX-Request')
    
    if form.validate_on_submit():
        try:
            # Create stipend
            stipend = Stipend(
                name=form.name.data,
                summary=form.summary.data,
                description=form.description.data,
                homepage_url=form.homepage_url.data,
                application_procedure=form.application_procedure.data,
                eligibility_criteria=form.eligibility_criteria.data,
                application_deadline=form.application_deadline.data,
                organization_id=form.organization_id.data,
                open_for_applications=form.open_for_applications.data
            )
            
            # Add tags
            for tag_id in form.tags.data:
                tag = Tag.query.get(tag_id)
                if tag:
                    stipend.tags.append(tag)
            
            db.session.add(stipend)
            db.session.commit()
            
            # Create audit log
            AuditLog.create(
                user_id=current_user.id,
                action='create_stipend',
                details=f"Created stipend: {stipend.name}",
                object_type='Stipend',
                object_id=stipend.id,
                ip_address=request.remote_addr
            )
            
            # Create notification
            Notification.create(
                type='STIPEND_CREATED',
                message=f'New stipend created: {stipend.name}',
                related_object=stipend
            )
            
            flash('Stipend created successfully', 'success')
            
            if is_htmx:
                return render_template('admin/stipends/_stipend_row.html', stipend=stipend), 200
            return redirect(url_for('admin.stipend.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating stipend: {str(e)}', 'error')
            if is_htmx:
                return render_template('admin/stipends/_form.html', form=form), 400
    
    return render_template('admin/stipends/create.html', form=form)
    """Create new stipend with HTMX support and audit logging"""
    form = StipendForm()
    is_htmx = request.headers.get('HX-Request')
    
    # Create audit log before operation
    AuditLog.create(
        user_id=current_user.id,
        action='create_stipend',
        details='Attempting to create new stipend',
        object_type='Stipend',
        ip_address=request.remote_addr
    )
    form = StipendForm()
    # Populate organization and tag choices
    organizations = Organization.query.order_by(Organization.name).all()
    tags = Tag.query.order_by(Tag.name).all()
    
    form.organization_id.choices = [(org.id, org.name) for org in organizations]
    form.tags.choices = [(tag.id, tag.name) for tag in tags]
    
    if request.method == 'POST':
        # Create audit log before operation
        AuditLog.create(
            user_id=current_user.id,
            action='create_stipend',
            details='Attempting to create new stipend',
            object_type='Stipend',
            ip_address=request.remote_addr
        )
    
    is_htmx = request.headers.get('HX-Request')

    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                # Audit log
                audit_log = AuditLog(
                    user_id=current_user.id,
                    action='create_stipend',
                    details=f"Attempt to create new stipend: {form.name.data}"
                )
                
                # Prepare stipend data
                stipend_data = {
                    'name': form.name.data,
                    'summary': form.summary.data,
                    'description': form.description.data,
                    'homepage_url': form.homepage_url.data,
                    'application_procedure': form.application_procedure.data,
                    'eligibility_criteria': form.eligibility_criteria.data,
                    'application_deadline': form.application_deadline.data if form.application_deadline.data else None,
                    'organization_id': form.organization_id.data,
                    'open_for_applications': form.open_for_applications.data,
                    'tags': [Tag.query.get(tag_id) for tag_id in form.tags.data]
                }
                
                new_stipend = create_stipend(stipend_data)
                flash_message(FlashMessages["CREATE_STIPEND_SUCCESS"], FlashCategory.SUCCESS)

                if is_htmx:
                    try:
                        # Add HTMX headers for better client-side handling
                        headers = {
                            'HX-Trigger': 'stipendCreated',
                            'HX-Reswap': 'outerHTML',
                            'HX-Retarget': '#stipend-table'
                        }
                        current_app.logger.debug(f"Attempting to render template at: admin/stipends/_stipend_row.html")
                        template_path = 'admin/stipends/_stipend_row.html'
                        current_app.logger.debug(f"Template exists: {current_app.jinja_env.loader.get_source(current_app.jinja_env, template_path) is not None}")
                        return render_template(template_path, stipend=new_stipend), 200, headers
                    except Exception as e:
                        current_app.logger.error(f"Failed to render stipend row template: {e}")
                        current_app.logger.error(f"Template path: {template_path}")
                        return render_template_string(
                            f"<tr><td colspan='6'>Error rendering new row: {str(e)}</td></tr>"
                        ), 200
                return redirect(url_for('admin.stipend.index'))

            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Failed to create stipend: {e}")
                flash_message(f"{FlashMessages.CREATE_STIPEND_ERROR.value}: {str(e)}", FlashCategory.ERROR)
                if is_htmx:
                    return render_template(
                        'admin/stipends/_form.html',
                        form=form,
                        error_messages=[str(e)],
                        field_errors={'application_deadline': [str(e)]},
                        is_htmx=True
                    ), 400
                return render_template('admin/stipends/create.html', form=form), 400
        else:
            current_app.logger.debug(f"Form validation failed: {form.errors}")
            if is_htmx:
                # Return HTMX response with form errors
                return render_template(
                    'admin/stipends/_form.html',
                    form=form,
                    is_htmx=True
                ), 400, {
                    'HX-Retarget': '#stipend-form-container',
                    'HX-Reswap': 'innerHTML'
                }
            return render_template('admin/stipends/create.html', form=form), 400

    notification_count = get_notification_count(current_user.id)
    return render_template('admin/stipends/create.html', 
                         form=form,
                         notification_count=notification_count)


@admin_stipend_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
@login_required
@admin_required
def edit(id):
    """Edit stipend with audit logging and notifications"""
    stipend = get_stipend_by_id(id)
    if not stipend:
        flash_message(FlashMessages.STIPEND_NOT_FOUND, FlashCategory.ERROR)
        return redirect(url_for('admin.stipend.index'))

    form = StipendForm(obj=stipend)
    is_htmx = request.headers.get('HX-Request')

    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                # Prepare update data directly from form
                stipend_data = {
                    'name': form.name.data,
                    'summary': form.summary.data,
                    'description': form.description.data,
                    'homepage_url': form.homepage_url.data,
                    'application_procedure': form.application_procedure.data,
                    'eligibility_criteria': form.eligibility_criteria.data,
                    'application_deadline': form.application_deadline.data,
                    'organization_id': form.organization_id.data,
                    'open_for_applications': form.open_for_applications.data
                }
                
                # Get current state before update
                before_state = stipend.to_dict()
            
                # Update the stipend
                updated_stipend = update_stipend(stipend, stipend_data, session=db.session)
            
                # Create audit log
                log_audit(
                    user_id=current_user.id,
                    action='update_stipend',
                    object_type='Stipend',
                    object_id=stipend.id,
                    before=before_state,
                    after=updated_stipend.to_dict()
                )
            
                # Create notification
                create_notification(
                    type='stipend_updated',
                    message=f'Stipend updated: {updated_stipend.name}',
                    related_object=updated_stipend,
                    user_id=current_user.id
                )
                
                flash_message(FlashMessages.STIPEND_UPDATE_SUCCESS, FlashCategory.SUCCESS)
                
                if is_htmx:
                    try:
                        # Return the updated row with HTMX headers
                        return render_template(
                            'admin/stipends/_stipend_row.html', 
                            stipend=updated_stipend
                        ), 200, {
                            'HX-Retarget': '#stipend-table',
                            'HX-Reswap': 'outerHTML'
                        }
                    except Exception as e:
                        current_app.logger.error(f"Failed to render stipend row template: {e}")
                        return render_template_string(
                            f"<tr><td colspan='6'>Error rendering updated row: {str(e)}</td></tr>"
                        ), 200
                # For non-HTMX requests, redirect to index
                return redirect(url_for('admin.stipend.index'))

            except ValidationError as e:
                db.session.rollback()
                current_app.logger.error(f"Validation error updating stipend: {e}")
                flash_message(f"Validation error: {str(e)}", FlashCategory.ERROR)
            except IntegrityError as e:
                db.session.rollback()
                current_app.logger.error(f"Database error updating stipend: {e}")
                flash_message("Database integrity error occurred", FlashCategory.ERROR)
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Failed to update stipend: {e}")
                flash_message(FlashMessages.STIPEND_UPDATE_ERROR, FlashCategory.ERROR)
                if is_htmx:
                    return render_template(
                        'admin/stipends/_form.html',
                        form=form,
                        stipend=stipend,
                        error_messages=[str(e)],
                        field_errors={'application_deadline': [str(e)]},
                        is_htmx=True
                    ), 400
                return render_template('admin/stipends/form.html', form=form, stipend=stipend), 400
        else:
            error_messages = []
            field_errors = {}
            for field_name, errors in form.errors.items():
                field = getattr(form, field_name)
                field_errors[field_name] = []
                for error in errors:
                    msg = format_error_message(field, error)
                    error_messages.append(msg)
                    field_errors[field_name].append(msg)
                    flash_message(f"{FlashMessages.FORM_VALIDATION_ERROR}: {msg}", FlashCategory.ERROR)
                
            if is_htmx:
                return render_template(
                    'admin/stipends/_form.html',
                    form=form,
                    stipend=stipend,
                    error_messages=error_messages,
                    field_errors=field_errors,
                    is_htmx=True
                ), 400
            return render_template('admin/stipends/form.html', form=form, stipend=stipend), 400
    
    if is_htmx:
        # Return just the form for HTMX requests
        return render_template('admin/stipends/_form.html', form=form, stipend=stipend)
    # Return full page for regular requests
    return render_template('admin/stipends/form.html', form=form, stipend=stipend)


@admin_stipend_bp.route('/<int:id>/delete', methods=['POST'])
@limiter.limit("3 per minute")
@login_required
@admin_required
def delete(id):
    """Delete stipend with audit logging and notification"""
    """Delete stipend with audit logging and notification"""
    stipend = get_stipend_by_id(id)
    if not stipend:
        flash_message(FlashMessages["STIPEND_NOT_FOUND"], FlashCategory.ERROR)
        if request.headers.get('HX-Request'):
            return render_template('_flash_messages.html'), 404
        return redirect(url_for('admin.stipend.index'))

    try:
        # Create audit log before deletion
        log_audit(
            user_id=current_user.id,
            action='delete_stipend',
            object_type='Stipend',
            object_id=stipend.id,
            before=stipend.to_dict()
        )
        
        delete_stipend(stipend.id)
        
        # Create notification
        create_notification(
            type='stipend_deleted',
            message=f'Stipend deleted: {stipend.name}',
            related_object=stipend,
            user_id=current_user.id
        )
        
        flash_message(FlashMessages.STIPEND_DELETE_SUCCESS, FlashCategory.SUCCESS)
        if request.headers.get('HX-Request'):
            return render_template('_flash_messages.html'), 200
        return redirect(url_for('admin.stipend.index'))
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to delete stipend: {e}")
        flash_message(FlashMessages.STIPEND_DELETE_ERROR, FlashCategory.ERROR)
        if request.headers.get('HX-Request'):
            return render_template('_flash_messages.html'), 500
        return redirect(url_for('stipend.index'))


@admin_stipend_bp.route('/', methods=['GET'])
@login_required
@admin_required
def index():
    page = request.args.get('page', 1, type=int)
    stipends = Stipend.query.paginate(page=page, per_page=10, error_out=False)
    current_app.logger.info(f"Stipends fetched: {stipends.items}")  # Debug: Log the fetched stipends
    return render_template('admin/stipends/index.html', stipends=stipends)


@admin_stipend_bp.route('/paginate/<int:page>', methods=['GET'])
@login_required
@admin_required
def paginate(page):
    stipends = Stipend.query.paginate(page=page, per_page=10, error_out=False)
    return render_template('admin/stipends/_stipends_table.html', stipends=stipends)
