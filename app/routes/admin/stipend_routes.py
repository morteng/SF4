from datetime import datetime
import logging

from flask import Blueprint, render_template, redirect, url_for, request, current_app, render_template_string
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
from app.utils import admin_required, flash_message

admin_stipend_bp = Blueprint('stipend', __name__, url_prefix='/stipends')


@admin_stipend_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    form = StipendForm()
    # Populate organization and tag choices
    organizations = Organization.query.order_by(Organization.name).all()
    tags = Tag.query.order_by(Tag.name).all()
    
    form.organization_id.choices = [(org.id, org.name) for org in organizations]
    form.tags.choices = [(tag.id, tag.name) for tag in tags]
    
    # Add audit log
    if request.method == 'POST':
        audit_log = AuditLog(
            user_id=current_user.id,
            action='create_stipend',
            details=f"Attempt to create new stipend",
            timestamp=datetime.utcnow()
        )
        db.session.add(audit_log)
    
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
                        current_app.logger.debug(f"Attempting to render template at: admin/stipends/_stipend_row.html")
                        template_path = 'admin/stipends/_stipend_row.html'
                        current_app.logger.debug(f"Template exists: {current_app.jinja_env.loader.get_source(current_app.jinja_env, template_path) is not None}")
                        return render_template(template_path, stipend=new_stipend), 200
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

    return render_template('admin/stipends/create.html', form=form)


@admin_stipend_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    stipend = get_stipend_by_id(id)
    if not stipend:
        flash_message(FlashMessages["STIPEND_NOT_FOUND"], FlashCategory.ERROR)
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
                
                # Update the stipend
                updated_stipend = update_stipend(stipend, stipend_data, session=db.session)
                flash_message(FlashMessages["UPDATE_STIPEND_SUCCESS"], FlashCategory.SUCCESS)
                
                if is_htmx:
                    try:
                        # Return the updated row with HTMX headers
                        return render_template('admin/stipends/_stipend_row.html', stipend=updated_stipend), 200
                    except Exception as e:
                        current_app.logger.error(f"Failed to render stipend row template: {e}")
                        return render_template_string(
                            f"<tr><td colspan='6'>Error rendering updated row: {str(e)}</td></tr>"
                        ), 200
                # For non-HTMX requests, redirect to index
                return redirect(url_for('admin.stipend.index'))

            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Failed to update stipend: {e}")
                flash_message(str(e) if str(e) else FlashMessages["UPDATE_STIPEND_ERROR"], FlashCategory.ERROR)
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
                    flash_message(msg, FlashCategory.ERROR)
                
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
@login_required
@admin_required
def delete(id):
    stipend = get_stipend_by_id(id)
    if not stipend:
        flash_message(FlashMessages["STIPEND_NOT_FOUND"], FlashCategory.ERROR)
        if request.headers.get('HX-Request'):
            return render_template('_flash_messages.html'), 404
        return redirect(url_for('admin.stipend.index'))

    try:
        delete_stipend(stipend.id)
        flash_message(FlashMessages["DELETE_STIPEND_SUCCESS"], FlashCategory.SUCCESS)
        if request.headers.get('HX-Request'):
            return render_template('_flash_messages.html'), 200
        return redirect(url_for('admin.stipend.index'))
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to delete stipend: {e}")
        flash_message(FlashMessages["DELETE_STIPEND_ERROR"], FlashCategory.ERROR)
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
