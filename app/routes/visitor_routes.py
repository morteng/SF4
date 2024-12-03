from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required  
from app.forms.user_forms import LoginForm, RegisterForm
from app.models.user import User
from app.extensions import db

visitor_bp = Blueprint('visitor', __name__)

@visitor_bp.route('/', methods=['GET'])
def index():
    """Display the visitor home page."""
    return render_template('index.html')

@visitor_bp.route('/about', methods=['GET'])
def about():
    """Display the about page."""
    return render_template('about.html')

@visitor_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.stipend.index'))  # Adjusted endpoint
        else:
            return redirect(url_for('user.profile'))

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        print(f"User retrieved: {user}")
        if user:
            print("User found.")
            if user.check_password(password):
                print("Password matched.")
                login_user(user)
                flash('Login successful.', 'success')
                if user.is_admin:
                    return redirect(url_for('admin.stipend.index'))  # Adjusted endpoint
                else:
                    return redirect(url_for('user.profile'))
            else:
                print("Password mismatch.")
                flash('Invalid username or password.', 'danger')
        else:
            print("User not found.")
            flash('Invalid username or password.', 'danger')
    return render_template('login.html', form=form)

@visitor_bp.route('/register', methods=['GET', 'POST'])
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
        return redirect(url_for('visitor.login'))
    return render_template('register.html', form=form)

@visitor_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('visitor.index'))
