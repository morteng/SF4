from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.models.user import User
from werkzeug.security import check_password_hash

public_user_bp = Blueprint('public_user', __name__)

@public_user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('public_user.dashboard'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')

@public_user_bp.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('public_user.login'))

@public_user_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')
