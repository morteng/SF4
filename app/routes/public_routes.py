from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user, login_required  # Import login_required
from app.forms.user_forms import LoginForm
from app.models.user import User

public_bp = Blueprint('public', __name__)

@public_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # Redirect to admin dashboard if user is an admin, else redirect to user profile
        if current_user.is_admin:
            return redirect(url_for('admin.stipend.index'))  # Assuming the admin stipends index is the dashboard
        else:
            return redirect(url_for('user.profile'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        password = form.password.data
        if user and user.check_password(password):
            print(f"Login success for: {user.username}")
            # db.session.refresh(user)  # Ensure the user is bound to the session
            login_user(user)
            flash('Login successful.', 'success')
            # Redirect to admin dashboard if user is an admin, else redirect to user profile
            if current_user.is_admin:
                return redirect(url_for('admin.stipend.index'))  # Assuming the admin stipends index is the dashboard
            else:
                return redirect(url_for('user.profile'))
        else:
            print("Login failed.")
            flash('Invalid username or password.', 'danger')
    return render_template('login.html', form=form)

@public_bp.route('/')
def index():
    return render_template('index.html')

@public_bp.route('/logout')
@login_required  # Ensure the user is logged in to log out
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('public.index'))

# create register route AI!