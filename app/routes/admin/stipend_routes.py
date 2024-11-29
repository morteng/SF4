from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.forms.admin_forms import StipendForm
from app.services.stipend_service import get_all_stipends, delete_stipend, create_stipend, get_stipend_by_id

admin_stipend_bp = Blueprint('admin_stipend', __name__, url_prefix='/admin/stipends')

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
        new_stipend = create_stipend(form.data)
        flash('Stipend created successfully.', 'success')
        return redirect(url_for('admin_stipend.index'))
    return render_template('admin/stipend/create.html', form=form)
