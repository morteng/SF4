from flask import Blueprint, redirect, url_for, flash, render_template, request
from flask_login import login_required
from app.models.user import User
from app.services.user_service import get_user_by_id, delete_user
from app.extensions import db  # Import db here

admin_user_bp = Blueprint('admin_user', __name__, url_prefix='/admin/users')

@admin_user_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    user = get_user_by_id(id)
    if user:
        delete_user(user)
        flash('User deleted successfully.', 'success')
    else:
        flash('User not found.', 'danger')
    return redirect(url_for('admin_user.index'))

@admin_user_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    from app.forms.admin_forms import UserForm
    form = UserForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            is_admin=form.is_admin.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User created successfully.', 'success')
        return redirect(url_for('admin_user.index'))
    return render_template('admin/user_form.html', form=form)

@admin_user_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    user = get_user_by_id(id)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('admin_user.index'))
    
    from app.forms.admin_forms import UserForm
    form = UserForm(original_username=user.username, original_email=user.email, obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.is_admin = form.is_admin.data
        if form.password.data:
            user.set_password(form.password.data)
        db.session.commit()
        flash('User updated successfully.', 'success')
        return redirect(url_for('admin_user.index'))
    return render_template('admin/user_form.html', form=form)
