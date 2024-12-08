from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.forms.admin_forms import StipendForm
from app.services.stipend_service import create_stipend, get_stipend_by_id, update_stipend
from datetime import datetime

stipend_bp = Blueprint('admin_stipend', __name__, url_prefix='/admin/stipends')

@stipend_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if not current_user.is_admin:
        abort(403)
    
    form = StipendForm()
    
    if request.method == 'POST':
        deadline_str = form.application_deadline.data
        if deadline_str:
            try:
                deadline_dt = datetime.strptime(deadline_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                # If parsing fails, fallback to None
                deadline_dt = None
        else:
            deadline_dt = None

        new_stipend_data = {
            'name': form.name.data,
            'summary': form.summary.data or None,
            'description': form.description.data or None,
            'homepage_url': form.homepage_url.data or None,
            'application_procedure': form.application_procedure.data or None,
            'eligibility_criteria': form.eligibility_criteria.data or None,
            # Ensure application_deadline is a datetime object
            'application_deadline': deadline_dt,
            'open_for_applications': form.open_for_applications.data
        }
        
        new_stipend = create_stipend(new_stipend_data)
        
        if new_stipend:
            flash('Stipend created successfully.', 'success')
            return redirect(url_for('admin.admin_stipend.index'))
        else:
            flash('Stipend with this name already exists or invalid application deadline.', 'danger')
    else:
        print(f"Form errors: {form.errors}")  # Debugging statement
    
    return render_template('admin/stipend_form.html', form=form, action=url_for('admin.admin_stipend.create'))

@stipend_bp.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    if not current_user.is_admin:
        abort(403)
    stipend = get_stipend_by_id(id)
    if not stipend:
        flash('Stipend not found.', 'danger')
        return redirect(url_for('admin.admin_stipend.index'))
    
    form = StipendForm(obj=stipend, original_name=stipend.name)
    
    if request.method == 'POST':
        deadline_str = form.application_deadline.data
        if deadline_str:
            try:
                deadline_dt = datetime.strptime(deadline_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                # If parsing fails, fallback to None
                deadline_dt = None
        else:
            deadline_dt = None

        update_data = {
            'name': form.name.data,
            'summary': form.summary.data or stipend.summary,
            'description': form.description.data or stipend.description,
            'homepage_url': form.homepage_url.data or stipend.homepage_url,
            'application_procedure': form.application_procedure.data or stipend.application_procedure,
            'eligibility_criteria': form.eligibility_criteria.data or stipend.eligibility_criteria,
            # Ensure application_deadline is a datetime object
            'application_deadline': deadline_dt,
            'open_for_applications': form.open_for_applications.data
        }
        
        if update_stipend(stipend, update_data):
            flash('Stipend updated successfully.', 'success')
            return redirect(url_for('admin.admin_stipend.index'))
        else:
            flash('Invalid application deadline.', 'danger')
    else:
        print(f"Form errors: {form.errors}")  # Debugging statement
    
    return render_template('admin/stipend_form.html', form=form, stipend=stipend, action=url_for('admin.admin_stipend.update', id=id))
