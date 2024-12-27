from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from app.forms.user_forms import ProfileForm
from app.models.user import User  # Import the User model
from app.extensions import db  # Import the db from extensions
from app.constants import FlashMessages, FlashCategory

user_bp = Blueprint('user', __name__, url_prefix='/user')


@user_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    return render_template('user/profile.html', user=current_user)

@user_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm(original_username=current_user.username, original_email=current_user.email)
    
    if form.validate_on_submit():
        new_username = form.username.data
        existing_user = User.query.filter_by(username=new_username).first()
        if existing_user and existing_user.id != current_user.id:
            flash(FlashMessages.USERNAME_ALREADY_EXISTS.value, FlashCategory.ERROR.value)
            return redirect(url_for('user.edit_profile'))
        current_user.username = new_username
        current_user.email = form.email.data
        db.session.commit()
        flash(FlashMessages.PROFILE_UPDATE_SUCCESS.value, FlashCategory.SUCCESS.value)
        return redirect(url_for('user.profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    else:
        flash(FlashMessages.PROFILE_UPDATE_INVALID_DATA.value, FlashCategory.ERROR.value)
        print(f"Form errors: {form.errors}")  # Log form errors
    
    return render_template('user/edit_profile.html', form=form)
