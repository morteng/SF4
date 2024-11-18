from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.services.user_service import get_user_by_id, list_all_users

user_bp = Blueprint('admin_user', __name__)

@user_bp.route('/users')
@login_required
def list_users():
    users = list_all_users()
    return render_template('admin/user_list.html', users=users)

@user_bp.route('/users/<int:user_id>')
@login_required
def user_details(user_id):
    user = get_user_by_id(user_id)
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('admin_user.list_users'))
    return render_template('admin/user_details.html', user=user)

# Add other routes as needed
