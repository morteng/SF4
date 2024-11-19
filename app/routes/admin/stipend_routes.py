# app/routes/admin/stipend_routes.py

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from app.models.stipend import Stipend
from app.forms.admin_forms import StipendForm
from app.utils import admin_required
from app import db

admin_stipend_bp = Blueprint('admin_stipend', __name__, url_prefix='/admin/stipends')

@admin_stipend_bp.route('/')
@admin_required
def index():
    stipends = Stipend.query.all()
    return render_template('admin/stipends/index.html', stipends=stipends)

@admin_stipend_bp.route('/create', methods=['GET', 'POST'])
@admin_required
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
        db.session.add(stipend)
        db.session.commit()
        flash('Stipend created successfully.', 'success')
        return redirect(url_for('admin_stipend.index'))
    return render_template('admin/stipends/create.html', form=form)

@admin_stipend_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit(id):
    stipend = Stipend.query.get_or_404(id)
    form = StipendForm(obj=stipend)
    if form.validate_on_submit():
        form.populate_obj(stipend)
        db.session.commit()
        flash('Stipend updated successfully.', 'success')
        return redirect(url_for('admin_stipend.index'))
    return render_template('admin/stipends/edit.html', form=form, stipend=stipend)

@admin_stipend_bp.route('/delete/<int:id>', methods=['POST'])
@admin_required
def delete(id):
    stipend = Stipend.query.get_or_404(id)
    db.session.delete(stipend)
    db.session.commit()
    flash('Stipend deleted successfully.', 'success')
    return redirect(url_for('admin_stipend.index'))
