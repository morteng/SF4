from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from app.forms.admin_forms import UserForm
from app.services.user_service import create_user, get_user_by_id, get_all_users, update_user, delete_user

admin_user_bp = Blueprint('admin_user', __name__)

@admin_user_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
def create():
    form = UserForm()
    if form.validate_on_submit():
        user = create_user(form.data)
        return redirect(url_for('admin_user.index'))
    return render_template('admin/user_form.html', form=form)

@admin_user_bp.route('/users/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    user = get_user_by_id(id)
    if user:
        delete_user(user)
        return redirect(url_for('admin_user.index'))
    return "User not found", 404

@admin_user_bp.route('/users/', methods=['GET'])
@login_required
def index():
    users = get_all_users()
    return render_template('admin/user_dashboard.html', users=users)

@admin_user_bp.route('/users/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    user = get_user_by_id(id)
    if not user:
        return "User not found", 404
    form = UserForm(obj=user)
    if form.validate_on_submit():
        update_user(user, form.data)
        return redirect(url_for('admin_user.index'))
    return render_template('admin/user_form.html', form=form)
