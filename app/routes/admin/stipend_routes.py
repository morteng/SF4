from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import login_required, current_user
from app.forms.admin_forms import StipendForm
from app.services.stipend_service import create_stipend, get_all_stipends, delete_stipend, update_stipend, get_stipend_by_id
from datetime import datetime
from app.extensions import db  # Importing db from extensions
import logging

# Create the Blueprint instance
stipend_bp = Blueprint('admin_stipend', __name__, url_prefix='/admin/stipends')

@stipend_bp.route('/')
@login_required
def index():
    if not current_user.is_admin:
        abort(403)
    stipends = get_all_stipends()
    return render_template('admin/stipend/index.html', stipends=stipends)

@stipend_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if not current_user.is_admin:
        abort(403)
    form = StipendForm()
    if request.method == 'POST' and form.validate_on_submit():
        stipend_data = {
            'name': form.name.data,
            'summary': form.summary.data or None,
            'description': form.description.data or None,
            'homepage_url': form.homepage_url.data or None,
            'application_procedure': form.application_procedure.data or None,
            'eligibility_criteria': form.eligibility_criteria.data or None,
            'application_deadline': form.application_deadline.data,  # Ensure this is correctly formatted
            'open_for_applications': form.open_for_applications.data
        }
        stipend = create_stipend(stipend_data, db.session)
        if stipend:
            flash('Stipend created successfully.', 'success')
            return redirect(url_for('admin_stipend.index'))
        else:
            flash('Failed to create stipend.', 'danger')
    else:
        logging.debug(f"Form errors: {form.errors}")
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", 'danger')
    return render_template('admin/stipend_form.html', form=form, action=url_for('admin.admin_stipend.create'))

@stipend_bp.route('/<int:stipend_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(stipend_id):
    if not current_user.is_admin:
        abort(403)
    stipend = get_stipend_by_id(stipend_id)
    if stipend is None:
        flash('Stipend not found.', 'danger')
        return redirect(url_for('admin_stipend.index'))
    
    form = StipendForm(obj=stipend)
    if request.method == 'POST' and form.validate_on_submit():
        stipend_data = {
            'name': form.name.data,
            'summary': form.summary.data or stipend.summary,
            'description': form.description.data or stipend.description,
            'homepage_url': form.homepage_url.data or stipend.homepage_url,
            'application_procedure': form.application_procedure.data or stipend.application_procedure,
            'eligibility_criteria': form.eligibility_criteria.data or stipend.eligibility_criteria,
            'application_deadline': form.application_deadline.data,  
            'open_for_applications': form.open_for_applications.data
        }
        
        # Ensure the application deadline can be either a valid datetime object or None.
        if not form.validate_application_deadline(form.application_deadline):
            stipend_data['application_deadline'] = None
        
        updated = update_stipend(stipend, stipend_data)
        if updated:
            flash('Stipend updated successfully.', 'success')
            return redirect(url_for('admin_stipend.index'))
        else:
            flash('Failed to update stipend.', 'danger')
    else:
        logging.debug(f"Form errors: {form.errors}")
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", 'danger')
    return render_template('admin/stipend_form.html', form=form, action=url_for('admin_stipend.edit', stipend_id=stipend.id))
