from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required
from app.forms.admin_forms import UserForm
from app.services.user_service import get_user_by_id, delete_user, get_all_users, create_user, update_user

admin_user_bp = Blueprint('user', __name__, url_prefix='/users')

@admin_user_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = UserForm()
    if form.validate_on_submit():
        try:
            new_user = create_user(form.data)
            flash('User created successfully.', 'success')
            return redirect(url_for('admin.user.index'))
        except ValueError as e:
            flash(str(e), 'danger')
    return render_template('admin/users/create.html', form=form)

@admin_user_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    user = get_user_by_id(id)
    if user:
        delete_user(user)
        flash(f'User {user.username} deleted.', 'success')
    else:
        flash('User not found.', 'danger')
    return redirect(url_for('admin.user.index'))

@admin_user_bp.route('/', methods=['GET'])
@login_required
def index():
    users = get_all_users()
    return render_template('admin/users/index.html', users=users)

@admin_user_bp.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    user = get_user_by_id(id)  # Fetch user data
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('admin.user.index'))
    
    form = UserForm(obj=user)
    if request.method == 'POST' and form.validate_on_submit():
        update_user(user, form.data)
        flash('User updated successfully.', 'success')
        return redirect(url_for('admin.user.index'))
    
    return render_template('admin/users/_edit_row.html', form=form, user=user)
