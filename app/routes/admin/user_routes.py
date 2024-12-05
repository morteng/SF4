from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from app.forms.admin_forms import UserForm
from app.services.user_service import get_user_by_id, delete_user, get_all_users, create_user, update_user

admin_user_bp = Blueprint('admin_user', __name__, url_prefix='/admin/users')

@admin_user_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = UserForm()
    if form.validate_on_submit():
        try:
            new_user = create_user(form.data)
            flash('User created successfully.', 'success')
            return redirect(url_for('admin_user.index'))
        except ValueError as e:
            flash(str(e), 'danger')
    return render_template('admin/user/create.html', form=form)

@admin_user_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    """Delete a user by ID."""
    user = get_user_by_id(id)
    if user:
        delete_user(user)
        flash(f'User {user.username} deleted.', 'success')
    else:
        flash('User not found.', 'danger')
    return redirect(url_for('admin_user.index'))

@admin_user_bp.route('/', methods=['GET'])
@login_required
def index():
    """List all users."""
    users = get_all_users()
    return render_template('admin/user/index.html', users=users)

@admin_user_bp.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    user = get_user_by_id(id)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('admin_user.index'))
    form = UserForm(obj=user)
    if form.validate_on_submit():
        update_user(user, form.data)
        flash('User updated successfully.', 'success')
        return redirect(url_for('admin_user.index'))
    return render_template('admin/user/update.html', form=form, user=user)
