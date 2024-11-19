# app/routes/admin/user_routes.py

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user, login_user
from app.models.user import User
from app.forms.admin_forms import UserForm
from app.extensions import db
from app.utils import admin_required

admin_user_bp = Blueprint('admin_user', __name__, url_prefix='/admin/users')

@admin_user_bp.route('/')
@admin_required
def index():
    users = User.query.all()
    return render_template('admin/users/index.html', users=users)

@admin_user_bp.route('/create', methods=['GET', 'POST'])
@admin_required
def create():
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
    return render_template('admin/users/create.html', form=form)

@admin_user_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit(id):
    user = User.query.get_or_404(id)
    form = UserForm(obj=user)
    if form.validate_on_submit():
        form.populate_obj(user)
        if form.password.data:
            user.set_password(form.password.data)
        db.session.commit()
        flash('User updated successfully.', 'success')
        return redirect(url_for('admin_user.index'))
    return render_template('admin/users/edit.html', form=form, user=user)

@admin_user_bp.route('/delete/<int:id>', methods=['POST'])
@admin_required
def delete(id):
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin_user.index'))
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully.', 'success')
    return redirect(url_for('admin_user.index'))
