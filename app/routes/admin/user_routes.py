from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from ..forms.admin_forms import UserForm  # Corrected import path
from ..models.user import User
from ..services.user_service import get_user_by_id
from app import db  # Correctly import db from app

admin_user_bp = Blueprint('admin_user', __name__, url_prefix='/users')

@admin_user_bp.route('/')
@login_required
def index():
    users = User.query.all()
    return render_template('admin/user_index.html', users=users)

@admin_user_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = UserForm()
    if form.validate_on_submit():
        new_user = User(
            username=form.username.data,
            email=form.email.data
        )
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('User created successfully!', 'success')
        return redirect(url_for('admin_user.index'))
    return render_template('admin/user_form.html', form=form, title='Create User')

@admin_user_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    user = get_user_by_id(id)
    if user is None:
        flash('User not found!', 'danger')
        return redirect(url_for('admin_user.index'))
    
    form = UserForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        
        if form.password.data:
            user.set_password(form.password.data)
        
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin_user.index'))
    return render_template('admin/user_form.html', form=form, title='Edit User')

@admin_user_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    user = get_user_by_id(id)
    if user is None:
        flash('User not found!', 'danger')
        return redirect(url_for('admin_user.index'))
    
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('admin_user.index'))
