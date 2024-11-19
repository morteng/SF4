from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, current_user, login_required  # Added this line
from app.models.user import User
from app.forms.user_forms import LoginForm

admin_auth_bp = Blueprint('admin_auth', __name__, url_prefix='/admin')

@admin_auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful.', 'success')
            return redirect(url_for('admin.index'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('admin/auth/login.html', form=form)

@admin_auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin.index'))
