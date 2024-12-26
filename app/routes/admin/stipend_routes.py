from datetime import datetime
import logging

from flask import Blueprint, render_template, redirect, url_for, request, current_app
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
            # Add organization validation
            organization = get_organization_by_id(form.organization_id.data)
            if not organization:
                flash_message(FLASH_MESSAGES["INVALID_ORGANIZATION"], FLASH_CATEGORY_ERROR)
                return render_template('admin/stipends/create.html', form=form), 200
            # Prepare form data
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
                return render_template('admin/stipends/_stipend_row.html', stipend=new_stipend)
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
                # Include the field label in the error message
                field_label = getattr(form, field).label.text
                error_message = f"{field_label}: {error}"
                flash_message(error_message, FLASH_CATEGORY_ERROR)
                # Ensure error message is included in response for HTMX
                if is_htmx and field == 'application_deadline':
                    return render_template('admin/stipends/create.html', form=form, error_message=error_message), 200
        # Return 200 status code for HTMX requests even with validation errors
        status_code = 200 if is_htmx else 400
        return render_template('admin/stipends/create.html', form=form), status_code

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

    if request.method == 'POST' and form.validate_on_submit():
        try:
            # Prepare update data
            stipend_data = {k: v for k, v in form.data.items() if k not in ('submit', 'csrf_token')}

            # Handle organization_id
            if 'organization_id' in stipend_data:
                organization = get_organization_by_id(stipend_data['organization_id'])
                if not organization:
                    flash_message(FLASH_MESSAGES["INVALID_ORGANIZATION"], FLASH_CATEGORY_ERROR)
                    return render_template('admin/stipends/form.html', form=form, stipend=stipend), 200

            # Handle empty application_deadline
            if stipend_data.get('application_deadline') == '':
                stipend_data['application_deadline'] = None

            # Update the stipend
            if update_stipend(stipend, stipend_data, session=db.session):
                flash_message(FLASH_MESSAGES["UPDATE_STIPEND_SUCCESS"], FLASH_CATEGORY_SUCCESS)
                return redirect(url_for('admin.stipend.index'))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Failed to update stipend: {e}")
            flash_message(str(e) if str(e) else FLASH_MESSAGES["UPDATE_STIPEND_ERROR"], FLASH_CATEGORY_ERROR)

    template = 'admin/stipends/_form.html' if request.headers.get('HX-Request') else 'admin/stipends/form.html'
    return render_template(template, form=form, stipend=stipend), 200


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
