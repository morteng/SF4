from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models.user import User
from app.forms.user_forms import ProfileForm
from app.services.user_service import get_user_by_id

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/profile')
@login_required
def profile():
    user = current_user
    return render_template('user/profile.html', user=user)

@user_bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm(original_username=current_user.username, original_email=current_user.email)
    if form.validate_on_submit():
        if form.username.data != current_user.username and User.query.filter_by(username=form.username.data).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('user.edit_profile'))
        
        if form.email.data != current_user.email and User.query.filter_by(email=form.email.data).first():
            flash('Email already exists!', 'danger')
            return redirect(url_for('user.edit_profile'))
        
        current_user.username = form.username.data
        current_user.email = form.email.data
        
        if form.password.data:
            current_user.set_password(form.password.data)
        
        from app import db
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('user.profile'))
    return render_template('user/edit_profile.html', form=form, title='Edit Profile')
