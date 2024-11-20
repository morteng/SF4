from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models.stipend import Stipend
from app.forms.admin_forms import StipendForm  # Corrected import path
from app.services.stipend_service import get_stipend_by_id, delete_stipend, get_all_stipends
from app.extensions import db  # Import db

admin_stipend_bp = Blueprint('admin_stipend', __name__, url_prefix='/admin/stipends')

@admin_stipend_bp.route('/list')
@login_required
def list_stipends():
    stipends = get_all_stipends()
    return render_template('admin/stipend/index.html', stipends=stipends)

@admin_stipend_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_stipend():
    form = StipendForm()
    if form.validate_on_submit():
        new_stipend = Stipend(
            name=form.name.data,
            summary=form.summary.data,
            description=form.description.data,
            homepage_url=form.homepage_url.data,
            application_procedure=form.application_procedure.data,
            eligibility_criteria=form.eligibility_criteria.data,
            application_deadline=form.application_deadline.data,
            open_for_applications=form.open_for_applications.data
        )
        db.session.add(new_stipend)
        db.session.commit()
        flash('Stipend created successfully', 'success')
        return redirect(url_for('admin_stipend.list_stipends'))
    return render_template('admin/stipend/create.html', form=form)

@admin_stipend_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_stipend(id):
    stipend = get_stipend_by_id(id)
    if stipend is None:
        flash('Stipend not found', 'danger')
        return redirect(url_for('admin_stipend.list_stipends'))
    
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
        flash('Stipend updated successfully', 'success')
        return redirect(url_for('admin_stipend.list_stipends'))
    
    return render_template('admin/stipend/edit.html', form=form)

@admin_stipend_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_stipend(id):
    stipend = get_stipend_by_id(id)
    if stipend is None:
        flash('Stipend not found', 'danger')
        return redirect(url_for('admin_stipend.list_stipends'))
    
    delete_stipend(stipend)
    flash('Stipend deleted successfully', 'success')
    return redirect(url_for('admin_stipend.list_stipends'))
