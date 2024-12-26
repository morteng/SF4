from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from app.forms.user_forms import ProfileForm
from app.models.user import User  # Import the User model
from app.extensions import db  # Import the db from extensions
from app.constants import FLASH_MESSAGES, FLASH_CATEGORY_ERROR

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
        
        # Check for duplicate username
        existing_user = User.query.filter_by(username=new_username).first()
        if existing_user and existing_user.id != current_user.id:
            flash(FLASH_MESSAGES["USERNAME_ALREADY_EXISTS"], FLASH_CATEGORY_ERROR)
            print(f"Flash message set: {FLASH_MESSAGES['USERNAME_ALREADY_EXISTS']} with category {FLASH_CATEGORY_ERROR}")
            return redirect(url_for('user.edit_profile'))
        
        current_user.username = new_username
        current_user.email = form.email.data
        
        # Update the user directly in the database
        db.session.commit()
        flash(FLASH_MESSAGES["PROFILE_UPDATE_SUCCESS"])
        print(f"Flash message set: {FLASH_MESSAGES['PROFILE_UPDATE_SUCCESS']}")
        return redirect(url_for('user.profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    else:
        flash(FLASH_MESSAGES["PROFILE_UPDATE_INVALID_DATA"], FLASH_CATEGORY_ERROR)
        print(f"Flash message set: {FLASH_MESSAGES['PROFILE_UPDATE_INVALID_DATA']} with category {FLASH_CATEGORY_ERROR}")
    return render_template('user/edit_profile.html', form=form)
