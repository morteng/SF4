from flask import (
    Blueprint, request, redirect, url_for, 
    render_template, current_app, render_template_string
)
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from wtforms import ValidationError
from app.extensions import limiter, db
from app.controllers.base_route_controller import BaseRouteController
from app.services.stipend_service import StipendService
from app.forms.admin_forms import StipendForm
from app.utils import (
    admin_required, flash_message, 
    log_audit, create_notification,
    format_error_message
)
from app.models import Stipend, Organization, Tag
from app.constants import FlashMessages, FlashCategory

def get_stipend_by_id(id):
    return Stipend.query.get_or_404(id)

def update_stipend(stipend, data, session=None):
    session = session or db.session
    try:
        for key, value in data.items():
            setattr(stipend, key, value)
        session.commit()
        return stipend
    except Exception as e:
        session.rollback()
        raise e

def delete_stipend(id):
    stipend = get_stipend_by_id(id)
    db.session.delete(stipend)
    db.session.commit()

admin_stipend_bp = Blueprint('stipend', __name__, url_prefix='/stipends')
stipend_controller = BaseRouteController(
    StipendService(),
    'stipend',
    StipendForm,
    'admin/stipends'
)

@admin_stipend_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    return stipend_controller.create()

@admin_stipend_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    return stipend_controller.edit(id)

@admin_stipend_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(id):
    return stipend_controller.delete(id)


@admin_stipend_bp.route('/create', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
@login_required
@admin_required
def create():
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
                'summary': form.summary.data if form.summary.data else None,
                'description': form.description.data if form.description.data else None,
                'homepage_url': form.homepage_url.data if form.homepage_url.data else None,
                'application_procedure': form.application_procedure.data if form.application_procedure.data else None,
                'eligibility_criteria': form.eligibility_criteria.data if form.eligibility_criteria.data else None,
                'application_deadline': form.application_deadline.data if form.application_deadline.data else None,
                'organization_id': form.organization_id.data if form.organization_id.data else None,
                'open_for_applications': form.open_for_applications.data,
                'tags': [Tag.query.get(tag_id) for tag_id in form.tags.data] if form.tags.data else []
            }
            
            # Create stipend
            stipend = Stipend.create(stipend_data, user_id=current_user.id)
            
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
                return '', 204, {'HX-Redirect': url_for('admin.stipend.index')}
            return redirect(url_for('admin.stipend.index'))
            
        except ValueError as e:
            db.session.rollback()
            current_app.logger.error(f"Validation error creating stipend: {str(e)}")
            flash_message(f"Validation error: {str(e)}", FlashCategory.ERROR)
            if is_htmx:
                return render_template('admin/stipends/_form.html', form=form)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating stipend: {str(e)}")
            flash_message(f"{FlashMessages.STIPEND_CREATE_ERROR}: {str(e)}", FlashCategory.ERROR)
            if is_htmx:
                return render_template('admin/stipends/_form.html', form=form)
    
    if is_htmx:
        return render_template('admin/stipends/_form.html', form=form)
    return render_template('admin/stipends/create.html', form=form)


@admin_stipend_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
@login_required
@admin_required
def edit(id):
    """Edit stipend with validation, audit logging, and notifications"""
    try:
        stipend = get_stipend_by_id(id)
        if not stipend:
            flash_message(FlashMessages.STIPEND_NOT_FOUND, FlashCategory.ERROR)
            return redirect(url_for('admin.stipend.index'))

        form = StipendForm(obj=stipend)
        is_htmx = request.headers.get('HX-Request')

        # Initialize form choices
        organizations = Organization.query.order_by(Organization.name).all()
        tags = Tag.query.order_by(Tag.name).all()
        form.organization_id.choices = [(org.id, org.name) for org in organizations]
        form.tags.choices = [(tag.id, tag.name) for tag in tags]

        if form.validate_on_submit():
            # Get current state before update
            before_state = stipend.to_dict()
            
            # Prepare update data
            update_data = {
                'name': form.name.data,
                'summary': form.summary.data,
                'description': form.description.data,
                'homepage_url': form.homepage_url.data,
                'application_procedure': form.application_procedure.data,
                'eligibility_criteria': form.eligibility_criteria.data,
                'application_deadline': form.application_deadline.data,
                'organization_id': form.organization_id.data,
                'open_for_applications': form.open_for_applications.data,
                'tags': form.tags.data
            }

            # Update stipend
            updated_stipend = stipend.update(update_data, user_id=current_user.id)
            
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
                return render_template('admin/stipends/_stipend_row.html', stipend=updated_stipend), 200, {
                    'HX-Trigger': 'stipendUpdated'
                }
            return redirect(url_for('admin.stipend.index'))
            
        return render_template('admin/stipends/edit.html', form=form, stipend=stipend)
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating stipend: {str(e)}")
        flash_message(f"{FlashMessages.STIPEND_UPDATE_ERROR}: {str(e)}", FlashCategory.ERROR)
        if is_htmx:
            return render_template('admin/stipends/_form.html', form=form, stipend=stipend), 400
        return render_template('admin/stipends/edit.html', form=form, stipend=stipend), 400
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
    """Delete stipend with validation, audit logging, and notifications"""
    try:
        stipend = get_stipend_by_id(id)
        if not stipend:
            flash_message(FlashMessages.STIPEND_NOT_FOUND, FlashCategory.ERROR)
            if request.headers.get('HX-Request'):
                return render_template('_flash_messages.html'), 404
            return redirect(url_for('admin.stipend.index'))

        # Create audit log before deletion
        log_audit(
            user_id=current_user.id,
            action='delete_stipend',
            object_type='Stipend',
            object_id=stipend.id,
            before=stipend.to_dict()
        )

        # Delete stipend
        Stipend.delete(stipend.id)
        
        flash_message(FlashMessages.STIPEND_DELETE_SUCCESS, FlashCategory.SUCCESS)
        if request.headers.get('HX-Request'):
            return render_template('_flash_messages.html'), 200
        return redirect(url_for('admin.stipend.index'))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting stipend: {str(e)}")
        flash_message(f"{FlashMessages.STIPEND_DELETE_ERROR}: {str(e)}", FlashCategory.ERROR)
        if request.headers.get('HX-Request'):
            return render_template('_flash_messages.html'), 500
        return redirect(url_for('admin.stipend.index'))
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
    return render_template('admin/stipends/index.html', 
                         stipends=stipends,
                         current_page=stipends.page,
                         total_pages=stipends.pages)


@admin_stipend_bp.route('/paginate', methods=['GET'])
@login_required
@admin_required
def paginate():
    page = request.args.get('page', 1, type=int)
    stipends = Stipend.query.paginate(page=page, per_page=10, error_out=False)
    return render_template('admin/stipends/_stipends_table.html', stipends=stipends)
