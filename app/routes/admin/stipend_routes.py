from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from app.forms.admin_forms import StipendForm
from app.services.stipend_service import get_all_stipends, delete_stipend, create_stipend, get_stipend_by_id, update_stipend
# AI: add docstrings to each class, method and function
admin_stipend_bp = Blueprint('admin_stipend', __name__)

@admin_stipend_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = StipendForm()
    if form.validate_on_submit():
        new_stipend = create_stipend(form.data)
        flash('Stipend created successfully.', 'success')
        return redirect(url_for('admin_stipend.index'))
    return render_template('admin/stipend/create.html', form=form)

@admin_stipend_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    stipend = get_stipend_by_id(id)
    if stipend:
        delete_stipend(stipend)
        flash('Stipend deleted.', 'success')
    else:
        flash('Stipend not found.', 'danger')
    return redirect(url_for('admin_stipend.index'))

@admin_stipend_bp.route('/', methods=['GET'])
@login_required
def index():
    stipends = get_all_stipends()
    return render_template('admin/stipend/index.html', stipends=stipends)

@admin_stipend_bp.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    stipend = get_stipend_by_id(id)
    if not stipend:
        flash('Stipend not found.', 'danger')
        return redirect(url_for('admin_stipend.index'))
    form = StipendForm(obj=stipend)
    if form.validate_on_submit():
        update_stipend(stipend, form.data)
        flash('Stipend updated successfully.', 'success')
        return redirect(url_for('admin_stipend.index'))
    return render_template('admin/stipend/update.html', form=form, stipend=stipend)
