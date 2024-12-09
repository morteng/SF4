from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.forms.admin_forms import StipendEditForm, StipendForm
from app.models.stipend import Stipend
from app.services.stipend_service import create_stipend, get_stipend_by_id, update_stipend, delete_stipend, get_all_stipends

admin_stipend_bp = Blueprint('admin_stipend', __name__, url_prefix='/stipends')

@admin_stipend_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = StipendForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        new_stipend_data = {
            'name': form.name.data,
            'summary': form.summary.data or None,
            'description': form.description.data or None,
            'homepage_url': form.homepage_url.data or None,
            'application_procedure': form.application_procedure.data or None,
            'eligibility_criteria': form.eligibility_criteria.data or None,
            'application_deadline': form.application_deadline.data or None,  # Explicitly handle blank or None values
            'open_for_applications': form.open_for_applications.data
        }
        
        stipend = create_stipend(new_stipend_data)
        
        if stipend:
            flash('Stipend created successfully!', 'success')
            return redirect(url_for('admin.admin_stipend.index'))
        else:
            flash('Stipend with this name already exists or invalid application deadline.', 'danger')
    else:
        print(f"Form errors: {form.errors}")  # Debugging statement
    
    return render_template('admin/stipend_form.html', form=form)

@admin_stipend_bp.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    stipend = get_stipend_by_id(id)
    if not stipend:
        flash('Stipend not found!', 'danger')
        return redirect(url_for('admin.admin_stipend.index'))
    
    form = StipendEditForm(obj=stipend)
    
    if request.method == 'POST' and form.validate_on_submit():
        updated_data = {
            'name': form.name.data,
            'summary': form.summary.data or stipend.summary,
            'description': form.description.data or stipend.description,
            'homepage_url': form.homepage_url.data or stipend.homepage_url,
            'application_procedure': form.application_procedure.data or stipend.application_procedure,
            'eligibility_criteria': form.eligibility_criteria.data or stipend.eligibility_criteria,
            'application_deadline': form.application_deadline.data or None,  # Explicitly handle blank or None values
            'open_for_applications': form.open_for_applications.data
        }
        
        update_stipend(stipend, updated_data)
        
        flash('Stipend updated successfully!', 'success')
        return redirect(url_for('admin.admin_stipend.index'))
    
    return render_template('admin/stipend_form.html', form=form)

@admin_stipend_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    stipend = get_stipend_by_id(id)
    if not stipend:
        flash('Stipend not found!', 'danger')
        return redirect(url_for('admin.admin_stipend.index'))
    
    delete_stipend(stipend)
    
    flash('Stipend deleted successfully!', 'success')
    return redirect(url_for('admin.admin_stipend.index'))

@admin_stipend_bp.route('/', methods=['GET'])
@login_required
def index():
    stipends = get_all_stipends()
    return render_template('admin/stipend/index.html', stipends=stipends)
