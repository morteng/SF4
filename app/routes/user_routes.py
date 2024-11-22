from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.forms.user_forms import ProfileForm  # Import ProfileForm
from app.extensions import db  # Import db

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    """Display the user's profile."""
    return render_template('user/profile.html', user=current_user)

@user_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def profile_edit():  # Renamed from edit_profile to profile_edit for consistency
    """Edit the user's profile."""
    form = ProfileForm(original_username=current_user.username, original_email=current_user.email)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('routes.user.profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('user/edit_profile.html', form=form)
