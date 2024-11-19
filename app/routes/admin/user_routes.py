from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models.user import User
from app.forms.admin_forms import UserForm
from app.services.user_service import get_user_by_id, delete_user

admin_user_bp = Blueprint('admin_user', __name__, url_prefix='/admin/users')

@admin_user_bp.route('/')
@login_required
def index():
    from app import db
    users = User.query.all()
    return render_template('admin/user_index.html', users=users)

@admin_user_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = UserForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            is_admin=form.is_admin.data
        )
        user.set_password(form.password.data)
        from app import db
        db.session.add(user)
        db.session.commit()
        flash('User created successfully!', 'success')
        return redirect(url_for('admin_user.index'))
    return render_template('admin/user_form.html', form=form, title='Create User')

@admin_user_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    user = get_user_by_id(id)
    if not user:
        flash('User not found!', 'danger')
        return redirect(url_for('admin_user.index'))
    
    form = UserForm(original_username=user.username, original_email=user.email, obj=user)
    if form.validate_on_submit():
        if form.username.data != user.username and User.query.filter_by(username=form.username.data).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('admin_user.edit', id=id))
        
        if form.email.data != user.email and User.query.filter_by(email=form.email.data).first():
            flash('Email already exists!', 'danger')
            return redirect(url_for('admin_user.edit', id=id))
        
        user.username = form.username.data
        user.email = form.email.data
        user.is_admin = form.is_admin.data
        
        if form.password.data:
            user.set_password(form.password.data)
        
        from app import db
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin_user.index'))
    return render_template('admin/user_form.html', form=form, title='Edit User')

@admin_user_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    user = get_user_by_id(id)
    if not user:
        flash('User not found!', 'danger')
        return redirect(url_for('admin_user.index'))
    
    try:
        delete_user(user)
        from app import db
        db.session.commit()
        flash('User deleted successfully!', 'success')
    except Exception as e:
        flash(f'Failed to delete user: {str(e)}', 'danger')
    
    return redirect(url_for('admin_user.index'))
