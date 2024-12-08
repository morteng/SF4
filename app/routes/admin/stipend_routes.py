from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from app.forms.admin_forms import StipendForm
from app.services.stipend_service import get_all_stipends, delete_stipend, create_stipend, get_stipend_by_id, update_stipend
from datetime import datetime

stipend_bp = Blueprint('admin_stipend', __name__, url_prefix='/stipends')

@stipend_bp.route('/', methods=['GET'])
@login_required
def index():
    if not current_user.is_admin:
        abort(403)
    stipends = get_all_stipends()
    return render_template('admin/stipend/index.html', stipends=stipends)

@stipend_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    if not current_user.is_admin:
        abort(403)
    stipend = get_stipend_by_id(id)
    if stipend:
        delete_stipend(stipend)
        flash('Stipend deleted.', 'success')
    else:
        flash('Stipend not found.', 'danger')
    return redirect(url_for('admin.admin_stipend.index'))

@stipend_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if not current_user.is_admin:
        abort(403)
    form = StipendForm()
    
    if request.method == 'POST':
        # Ensure application_deadline is a string
        stipend_data = {
            'name': request.form.get('name'),
            'summary': request.form.get('summary') or None,
            'description': request.form.get('description') or None,
            'homepage_url': request.form.get('homepage_url') or None,
            'application_procedure': request.form.get('application_procedure') or None,
            'eligibility_criteria': request.form.get('eligibility_criteria') or None,
            'application_deadline': request.form.get('application_deadline'),
            'open_for_applications': request.form.get('open_for_applications', type=bool)
        }
        
        form = StipendForm(data=stipend_data)
    
    if form.validate_on_submit():
        print("Form validated successfully!")
        print("Form data after validation:", form.data)  # Debugging statement
        
        new_stipend_data = {
            'name': form.name.data,
            'summary': form.summary.data or None,
            'description': form.description.data or None,
            'homepage_url': form.homepage_url.data or None,
            'application_procedure': form.application_procedure.data or None,
            'eligibility_criteria': form.eligibility_criteria.data or None,
            # Ensure application_deadline is a datetime object
            'application_deadline': form.application_deadline.data if isinstance(form.application_deadline.data, datetime) else None,
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
    
    form = StipendForm(obj=stipend)
    
    if request.method == 'POST':
        # Ensure application_deadline is a string
        update_data = {
            'name': request.form.get('name'),
            'summary': request.form.get('summary') or stipend.summary,
            'description': request.form.get('description') or stipend.description,
            'homepage_url': request.form.get('homepage_url') or stipend.homepage_url,
            'application_procedure': request.form.get('application_procedure') or stipend.application_procedure,
            'eligibility_criteria': request.form.get('eligibility_criteria') or stipend.eligibility_criteria,
            'application_deadline': request.form.get('application_deadline'),
            'open_for_applications': request.form.get('open_for_applications', type=bool)
        }
        
        form = StipendForm(data=update_data)
    
    if form.validate_on_submit():
        print("Form validated successfully!")
        print("Form data after validation:", form.data)  # Debugging statement
        
        update_data = {
            'name': form.name.data,
            'summary': form.summary.data or stipend.summary,
            'description': form.description.data or stipend.description,
            'homepage_url': form.homepage_url.data or stipend.homepage_url,
            'application_procedure': form.application_procedure.data or stipend.application_procedure,
            'eligibility_criteria': form.eligibility_criteria.data or stipend.eligibility_criteria,
            # Ensure application_deadline is a datetime object
            'application_deadline': form.application_deadline.data if isinstance(form.application_deadline.data, datetime) else None,
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
