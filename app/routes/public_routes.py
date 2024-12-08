from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required  
from app.forms.user_forms import LoginForm, RegisterForm
from app.models.user import User
from app.extensions import db

public_bp = Blueprint('public', __name__)

@public_bp.route('/', methods=['GET'])
def index():
    """Display the visitor home page."""
    return render_template('index.html')

@public_bp.route('/about', methods=['GET'])
def about():
    """Display the about page."""
    return render_template('about.html')

@public_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        # Redirect to admin dashboard if user is an admin, else redirect to user profile
        if current_user.is_admin:
            return redirect(url_for('admin.admin_stipend.index'))  # Assuming the admin stipends index is the dashboard
        else:
            return redirect(url_for('user.profile'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful.', 'success')
            print(f"User {user.username} logged in successfully.")  # Debugging statement
            # Redirect to admin dashboard if user is an admin, else redirect to user profile
            if current_user.is_admin:
                return redirect(url_for('admin.admin_stipend.index'))  # Assuming the admin stipends index is the dashboard
            else:
                return redirect(url_for('user.profile'))
        else:
            flash('Invalid username or password.', 'danger')
    print(f"Form data: {form.data}")  # Debugging statement
    print(f"Form errors: {form.errors}")  # Debugging statement
    return render_template('login.html', form=form)

@public_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if current_user.is_authenticated:
        return redirect(url_for('user.profile'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('public.login'))
    return render_template('register.html', form=form)

@public_bp.route('/logout', methods=['GET'])
def logout():
    """Handle user logout."""
    print(f"Request method: {request.method}")  # Debugging statement
    if request.method == 'GET':
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('public.index'))
    else:
        return "Method not allowed", 405
