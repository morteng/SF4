from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, login_required
from app.forms.user_forms import ProfileForm, LoginForm
from app.models.user import User  # Import the User model
from app.extensions import db  # Import the db from extensions

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Logged in successfully.')
            # Redirect based on user role
            if current_user.is_admin:
                return redirect(url_for('admin.dashboard.dashboard'))
            else:
                return redirect(url_for('user.profile'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html', form=form)

@user_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    return render_template('user/profile.html', user=current_user)

@user_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm(original_username=current_user.username, original_email=current_user.email)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        # Update the user directly in the database
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('user.profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('user/edit_profile.html', form=form)
