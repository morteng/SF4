from datetime import datetime
import logging

from flask import Blueprint, render_template, redirect, url_for, request, current_app, render_template_string
from flask_login import login_required

from app.constants import (
    FLASH_CATEGORY_INFO,
    FLASH_MESSAGES,
    FLASH_CATEGORY_SUCCESS,
    FLASH_CATEGORY_ERROR
)
from app.forms.admin_forms import StipendForm, OrganizationForm
from app.models.stipend import Stipend
from app.models.organization import Organization
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
    is_htmx = request.headers.get('HX-Request')

    if form.validate_on_submit():
        try:
            # Prepare form data with explicit date handling
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
                
            # Create the stipend
            new_stipend = create_stipend(stipend_data)
            flash_message(FLASH_MESSAGES["CREATE_STIPEND_SUCCESS"], FLASH_CATEGORY_SUCCESS)

            if is_htmx:
                try:
                    # Ensure template path is correct
                    template_path = 'templates/admin/stipends/_stipend_row.html'
                    current_app.logger.debug(f"Attempting to render template at: {template_path}")
                    # Try rendering with full path first
                    try:
                        rendered = render_template(template_path, stipend=new_stipend)
                        # Add flash message to HTMX response
                        flash_message(FLASH_MESSAGES["CREATE_STIPEND_SUCCESS"], FLASH_CATEGORY_SUCCESS)
                        return rendered, 200
                    except TemplateNotFound:
                        # Try with relative path if full path fails
                        try:
                            rendered = render_template('admin/stipends/_stipend_row.html', stipend=new_stipend)
                            flash_message(FLASH_MESSAGES["CREATE_STIPEND_SUCCESS"], FLASH_CATEGORY_SUCCESS)
                            return rendered, 200
                        except Exception as e:
                            current_app.logger.error(f"Failed to render stipend row template: {e}")
                            # Return error message with flash
                            flash_message(f"Error rendering new row: {str(e)}", FLASH_CATEGORY_ERROR)
                            return render_template_string(
                                f"<tr><td colspan='6'>Error rendering new row: {str(e)}</td></tr>"
                            ), 200
                    except Exception as e:
                        current_app.logger.error(f"Failed to render stipend row template: {e}")
                        # Return error message with flash
                        flash_message(f"Error rendering new row: {str(e)}", FLASH_CATEGORY_ERROR)
                        return render_template_string(
                            f"<tr><td colspan='6'>Error rendering new row: {str(e)}</td></tr>"
                        ), 200
                return redirect(url_for('admin.stipend.index'))

            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Failed to create stipend: {e}")
                flash_message(str(e), FLASH_CATEGORY_ERROR)
                return render_template('admin/stipends/create.html', form=form), 400

    # Handle form validation errors
    if request.method == 'POST':
        for field, errors in form.errors.items():
            for error in errors:
                # Special handling for date field errors
                if field == 'application_deadline':
                    if 'Not a valid datetime value' in error:
                        error_msg = "Invalid date format. Please use YYYY-MM-DD HH:MM:SS"
                    elif 'cannot be in the past' in error:
                        error_msg = "Application deadline must be a future date"
                    elif 'cannot be more than 5 years' in error:
                        error_msg = "Application deadline cannot be more than 5 years in the future"
                    else:
                        error_msg = f"Invalid date: {error}"
                    
                    if is_htmx:
                        return render_template_string(error_msg), 400
                    flash_message(error_msg, FLASH_CATEGORY_ERROR)
                else:
                    # Include the field label in the error message
                    field_label = getattr(form, field).label.text
                    error_msg = f"{field_label}: {error}"
                    if is_htmx:
                        return render_template_string(error_msg), 400
                    flash_message(error_msg, FLASH_CATEGORY_ERROR)
        
        if is_htmx:
            return render_template_string("Invalid form data"), 400
        return render_template('admin/stipends/create.html', form=form), 400

    return render_template('admin/stipends/create.html', form=form)


@admin_stipend_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    stipend = get_stipend_by_id(id)
    if not stipend:
        flash_message(FLASH_MESSAGES["STIPEND_NOT_FOUND"], FLASH_CATEGORY_ERROR)
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
                flash_message(FLASH_MESSAGES["UPDATE_STIPEND_SUCCESS"], FLASH_CATEGORY_SUCCESS)
                
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
                flash_message(str(e) if str(e) else FLASH_MESSAGES["UPDATE_STIPEND_ERROR"], FLASH_CATEGORY_ERROR)
                return render_template('admin/stipends/form.html', form=form, stipend=stipend), 400
        else:
            # Handle form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    # Special handling for date field errors
                    if field == 'application_deadline':
                        if 'Not a valid datetime value' in error:
                            flash_message("Invalid date format. Please use YYYY-MM-DD HH:MM:SS", FLASH_CATEGORY_ERROR)
                        elif 'cannot be in the past' in error:
                            flash_message("Application deadline must be a future date", FLASH_CATEGORY_ERROR)
                        elif 'cannot be more than 5 years' in error:
                            flash_message("Application deadline cannot be more than 5 years in the future", FLASH_CATEGORY_ERROR)
                        else:
                            flash_message(f"Invalid date: {error}", FLASH_CATEGORY_ERROR)
                    else:
                        # Include the field label in the error message
                        field_label = getattr(form, field).label.text
                        flash_message(f"{field_label}: {error}", FLASH_CATEGORY_ERROR)
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
        flash_message(FLASH_MESSAGES["STIPEND_NOT_FOUND"], FLASH_CATEGORY_ERROR)
        if request.headers.get('HX-Request'):
            return render_template('_flash_messages.html'), 404
        return redirect(url_for('admin.stipend.index'))

    try:
        delete_stipend(stipend.id)
        flash_message(FLASH_MESSAGES["DELETE_STIPEND_SUCCESS"], FLASH_CATEGORY_SUCCESS)
        if request.headers.get('HX-Request'):
            return render_template('_flash_messages.html'), 200
        return redirect(url_for('admin.stipend.index'))
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to delete stipend: {e}")
        flash_message(FLASH_MESSAGES["DELETE_STIPEND_ERROR"], FLASH_CATEGORY_ERROR)
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
