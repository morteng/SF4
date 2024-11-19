from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models.stipend import Stipend
from app.forms.admin_forms import StipendForm
from app.services.stipend_service import get_stipend_by_id, delete_stipend

admin_stipend_bp = Blueprint('admin_stipend', __name__, url_prefix='/admin/stipends')

@admin_stipend_bp.route('/')
@login_required
def index():
    from app import db  # Import db within the function to avoid circular imports
    stipends = Stipend.query.all()
    return render_template('admin/stipend_index.html', stipends=stipends)

@admin_stipend_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = StipendForm()
    if form.validate_on_submit():
        stipend = Stipend(
            name=form.name.data,
            summary=form.summary.data,
            description=form.description.data,
            homepage_url=form.homepage_url.data,
            application_procedure=form.application_procedure.data,
            eligibility_criteria=form.eligibility_criteria.data,
            application_deadline=form.application_deadline.data,
            open_for_applications=form.open_for_applications.data
        )
        from app import db  # Import db within the function to avoid circular imports
        db.session.add(stipend)
        db.session.commit()
        flash('Stipend created successfully!', 'success')
        return redirect(url_for('admin_stipend.index'))
    return render_template('admin/stipend_form.html', form=form, title='Create Stipend')

@admin_stipend_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    stipend = get_stipend_by_id(id)
    if not stipend:
        flash('Stipend not found!', 'danger')
        return redirect(url_for('admin_stipend.index'))
    
    form = StipendForm(obj=stipend)
    if form.validate_on_submit():
        stipend.name = form.name.data
        stipend.summary = form.summary.data
        stipend.description = form.description.data
        stipend.homepage_url = form.homepage_url.data
        stipend.application_procedure = form.application_procedure.data
        stipend.eligibility_criteria = form.eligibility_criteria.data
        stipend.application_deadline = form.application_deadline.data
        stipend.open_for_applications = form.open_for_applications.data
        from app import db  # Import db within the function to avoid circular imports
        db.session.commit()
        flash('Stipend updated successfully!', 'success')
        return redirect(url_for('admin_stipend.index'))
    return render_template('admin/stipend_form.html', form=form, title='Edit Stipend')

@admin_stipend_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    stipend = get_stipend_by_id(id)
    if not stipend:
        flash('Stipend not found!', 'danger')
        return redirect(url_for('admin_stipend.index'))
    
    try:
        delete_stipend(stipend)
        from app import db  # Import db within the function to avoid circular imports
        db.session.commit()
        flash('Stipend deleted successfully!', 'success')
    except Exception as e:
        flash(f'Failed to delete stipend: {str(e)}', 'danger')
    
    return redirect(url_for('admin_stipend.index'))
