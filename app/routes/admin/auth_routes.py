from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app.forms.admin_forms import LoginForm
from app.models.user import User

admin_auth_bp = Blueprint('admin_auth', __name__, url_prefix='/admin/auth')

@admin_auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_stipend.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('admin_stipend.index'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('admin/login.html', form=form, title='Admin Login')

@admin_auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin_auth.login'))
