from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import login_required, current_user
from app.forms.admin_forms import StipendForm
from app.services.stipend_service import create_stipend, get_all_stipends, delete_stipend, update_stipend, get_stipend_by_id
from datetime import datetime
from app.extensions import db  # Importing db from extensions

admin_stipend = Blueprint('admin_stipend', __name__, url_prefix='/admin/stipends')

@admin_stipend.route('/')
@login_required
def index():
    if not current_user.is_admin:
        abort(403)
    stipends = get_all_stipends()
    return render_template('admin/stipends/index.html', stipends=stipends)

@admin_stipend.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if not current_user.is_admin:
        abort(403)
    form = StipendForm()
    if request.method == 'POST' and form.validate_on_submit():
        data = {
            'name': form.name.data,
            'summary': form.summary.data or None,
            'description': form.description.data or None,
            'homepage_url': form.homepage_url.data or None,
            'application_procedure': form.application_procedure.data or None,
            'eligibility_criteria': form.eligibility_criteria.data or None,
            'open_for_applications': form.open_for_applications.data
        }
        
        application_deadline = form.application_deadline.data
        if application_deadline:
            data['application_deadline'] = application_deadline
        
        stipend = create_stipend(data, db.session)
        if stipend:
            flash('Stipend created successfully.', 'success')
            return redirect(url_for('admin_stipend.index'))
        else:
            flash('Failed to create stipend.', 'danger')
    return render_template('admin/stipend_form.html', form=form, action=url_for('admin_stipend.create'))

@admin_stipend.route('/<int:stipend_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(stipend_id):
    if not current_user.is_admin:
        abort(403)
    stipend = get_stipend_by_id(stipend_id)
    if not stipend:
        flash('Stipend not found.', 'danger')
        return redirect(url_for('admin_stipend.index'))
    
    form = StipendForm(obj=stipend)
    if request.method == 'POST' and form.validate_on_submit():
        data = {
            'name': form.name.data,
            'summary': form.summary.data or stipend.summary,
            'description': form.description.data or stipend.description,
            'homepage_url': form.homepage_url.data or stipend.homepage_url,
            'application_procedure': form.application_procedure.data or stipend.application_procedure,
            'eligibility_criteria': form.eligibility_criteria.data or stipend.eligibility_criteria,
            'open_for_applications': form.open_for_applications.data
        }
        
        application_deadline = form.application_deadline.data
        if application_deadline:
            data['application_deadline'] = application_deadline
        
        success = update_stipend(stipend, data)
        if success:
            flash('Stipend updated successfully.', 'success')
            return redirect(url_for('admin_stipend.index'))
        else:
            flash('Failed to update stipend.', 'danger')
    return render_template('admin/stipend_form.html', form=form, action=url_for('admin_stipend.edit', stipend_id=stipend.id))

@admin_stipend.route('/<int:stipend_id>/delete', methods=['POST'])
@login_required
def delete(stipend_id):
    if not current_user.is_admin:
        abort(403)
    stipend = get_stipend_by_id(stipend_id)
    if not stipend:
        flash('Stipend not found.', 'danger')
        return redirect(url_for('admin_stipend.index'))
    
    delete_stipend(stipend, db.session)
    flash('Stipend deleted successfully.', 'success')
    return redirect(url_for('admin_stipend.index'))
