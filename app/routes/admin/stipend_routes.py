from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from app.forms.admin_forms import StipendForm
from app.services.stipend_service import get_all_stipends, delete_stipend, create_stipend, get_stipend_by_id, update_stipend

admin_stipend_bp = Blueprint('admin_stipend', __name__, url_prefix='/stipends')

@admin_stipend_bp.route('/', methods=['GET'])
@login_required
def index():
    if not current_user.is_admin:
        abort(403)
    stipends = get_all_stipends()
    return render_template('admin/stipend/index.html', stipends=stipends)

@admin_stipend_bp.route('/delete/<int:id>', methods=['POST'])
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
    return redirect(url_for('admin_stipend.index'))

@admin_stipend_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if not current_user.is_admin:
        abort(403)
    form = StipendForm()
    if form.validate_on_submit():
        new_stipend_data = {
            'name': form.name.data,
            'summary': form.summary.data or None,
            'description': form.description.data or None,
            'homepage_url': form.homepage_url.data or None,
            'application_procedure': form.application_procedure.data or None,
            'eligibility_criteria': form.eligibility_criteria.data or None,
            'application_deadline': form.application_deadline.data.strftime('%Y-%m-%d %H:%M:%S') if form.application_deadline.data else None,
            'open_for_applications': form.open_for_applications.data
        }
        print(f"Form data: {new_stipend_data}")  # Debugging statement
        new_stipend = create_stipend(new_stipend_data)
        if new_stipend:
            flash('Stipend created successfully.', 'success')
            return redirect(url_for('admin_stipend.index'))
        else:
            flash('Stipend with this name already exists or invalid application deadline.', 'danger')
    print(f"Form errors: {form.errors}")  # Debugging statement
    return render_template('admin/stipend/create.html', form=form)

@admin_stipend_bp.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    if not current_user.is_admin:
        abort(403)
    stipend = get_stipend_by_id(id)
    if not stipend:
        flash('Stipend not found.', 'danger')
        return redirect(url_for('admin_stipend.index'))
    form = StipendForm(obj=stipend)
    if form.validate_on_submit():
        update_data = {
            'name': form.name.data,
            'summary': form.summary.data or stipend.summary,
            'description': form.description.data or stipend.description,
            'homepage_url': form.homepage_url.data or stipend.homepage_url,
            'application_procedure': form.application_procedure.data or stipend.application_procedure,
            'eligibility_criteria': form.eligibility_criteria.data or stipend.eligibility_criteria,
            'application_deadline': form.application_deadline.data.strftime('%Y-%m-%d %H:%M:%S') if form.application_deadline.data else stipend.application_deadline,
            'open_for_applications': form.open_for_applications.data
        }
        if update_stipend(stipend, update_data):
            flash('Stipend updated successfully.', 'success')
            return redirect(url_for('admin_stipend.index'))
        else:
            flash('Invalid application deadline.', 'danger')
    return render_template('admin/stipend/update.html', form=form, stipend=stipend)
