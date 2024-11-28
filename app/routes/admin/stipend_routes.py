from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.services.stipend_service import get_all_stipends, delete_stipend

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
