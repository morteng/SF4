from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models.user import User
from app.forms.user_forms import ProfileForm
from app.services.user_service import get_user_by_id

user_bp = Blueprint('user', __name__)

@user_bp.route('/logout')
@login_required
def logout():
    # Logic for user logout
    pass

@user_bp.route('/profile')
@login_required
def profile():
    user = get_user_by_id(current_user.id)
    if user is None:
        flash('User not found', 'danger')
        return redirect(url_for('public.index'))
    return render_template('user/profile.html', user=user)

@user_bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = get_user_by_id(current_user.id)
    if user is None:
        flash('User not found', 'danger')
        return redirect(url_for('public.index'))
    
    form = ProfileForm(original_username=user.username, original_email=user.email)
    if form.validate_on_submit():
        # Logic to update user profile
        pass
    
    return render_template('user/edit_profile.html', form=form, user=user)
