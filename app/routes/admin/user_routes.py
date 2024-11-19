from flask import Blueprint, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from app.models.user import User
from app.utils import login_required  # Import the login_required decorator

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password) and user.is_admin:
        session['user_id'] = user.id
        return redirect(url_for('admin.dashboard'))
    else:
        flash('Invalid username or password')
        return redirect(url_for('admin.login')), 401

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    return "Admin Dashboard"
