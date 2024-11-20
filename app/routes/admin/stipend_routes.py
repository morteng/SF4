from flask import Blueprint, redirect, url_for, flash, render_template, request
from flask_login import login_required
from app.models.stipend import Stipend
from app.services.stipend_service import get_stipend_by_id, delete_stipend
from app.extensions import db  # Import db here

# Ensure the blueprint is defined correctly
admin_stipend_bp = Blueprint('admin_stipend', __name__, url_prefix='/stipends')

@admin_stipend_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    stipend = get_stipend_by_id(id)
    if stipend:
        delete_stipend(stipend)
        flash('Stipend deleted successfully.', 'success')
    else:
        flash('Stipend not found.', 'danger')
    return redirect(url_for('admin_stipend.index'))

@admin_stipend_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    from app.forms.admin_forms import StipendForm
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
        db.session.add(stipend)
        db.session.commit()
        flash('Stipend created successfully.', 'success')
        return redirect(url_for('admin_stipend.index'))
    return render_template('admin/stipend_form.html', form=form)

@admin_stipend_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    stipend = get_stipend_by_id(id)
    if not stipend:
        flash('Stipend not found.', 'danger')
        return redirect(url_for('admin_stipend.index'))
    
    from app.forms.admin_forms import StipendForm
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
        db.session.commit()
        flash('Stipend updated successfully.', 'success')
        return redirect(url_for('admin_stipend.index'))
    return render_template('admin/stipend_form.html', form=form)

@admin_stipend_bp.route('/')
@login_required
def index():
    # Assuming there's a method to get all stipends, let's add it here
    # For now, we'll just render an empty template
    stipends = Stipend.query.all()  # Fetch all stipends from the database
    return render_template('admin/stipend/index.html', stipends=stipends)
