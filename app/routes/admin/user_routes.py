from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from app.services.user_service import get_user_by_id, delete_user, get_all_users

user_bp = Blueprint('admin_user', __name__, url_prefix='/admin/users')

@user_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    user = get_user_by_id(id)
    if user:
        delete_user(user)
        flash(f'User {user.username} deleted.', 'success')
    else:
        flash('User not found.', 'danger')
    return redirect(url_for('admin_user.index'))

@user_bp.route('/', methods=['GET'])
@login_required
def index():
    users = get_all_users()
    return render_template('admin/user/index.html', users=users)
