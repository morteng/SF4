from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app.forms.user_forms import LoginForm
from app.models.user import User

# Ensure the blueprint name is 'auth_bp'
auth_bp = Blueprint('admin_auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_stipend.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('admin_stipend.index'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html', form=form)

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin_auth.login'))
