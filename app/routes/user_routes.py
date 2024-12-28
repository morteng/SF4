import logging
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user, login_required
from flask_wtf.csrf import CSRFError
from app.utils import flash_message
from app.forms.user_forms import ProfileForm
from app.models.user import User  # Import the User model
from app.extensions import db  # Import the db from extensions
from app.constants import FlashMessages, FlashCategory

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.errorhandler(CSRFError)
def handle_csrf_error(e):
    return FlashMessages.CSRF_INVALID.value, 400


@user_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    return render_template('user/profile.html', user=current_user)

@user_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm(original_username=current_user.username, original_email=current_user.email)
    
    if request.method == 'POST':
        # Validate CSRF token first
        if not form.validate():
            if 'csrf_token' in form.errors:
                logging.warning("Invalid CSRF token in profile update request")
                flash_message(FlashMessages.CSRF_INVALID, FlashCategory.ERROR)
                return render_template('user/edit_profile.html', form=form), 400
            
        if form.validate():
            try:
                # Check for existing username
                new_username = form.username.data
                existing_user = User.query.filter_by(username=new_username).first()
                if existing_user and existing_user.id != current_user.id:
                    logging.warning(f"Username already exists: {new_username}")
                    flash_message(FlashMessages.USERNAME_ALREADY_EXISTS, FlashCategory.ERROR)
                    return render_template('user/edit_profile.html', form=form), 400
                
                # Update user profile
                current_user.username = new_username
                current_user.email = form.email.data
                db.session.commit()
                logging.info(f"Profile updated successfully for user {current_user.id}")
                flash_message(FlashMessages.PROFILE_UPDATE_SUCCESS, FlashCategory.SUCCESS)
                return redirect(url_for('user.profile'))
            except Exception as e:
                db.session.rollback()
                logging.error(f"Error updating profile for user {current_user.id}: {str(e)}", exc_info=True)
                flash_message(FlashMessages.PROFILE_UPDATE_ERROR, FlashCategory.ERROR)
                return render_template('user/edit_profile.html', form=form), 500
        else:
            logging.warning(f"Profile form validation failed: {form.errors}")
            flash_message(FlashMessages.PROFILE_UPDATE_INVALID_DATA, FlashCategory.ERROR)
            return render_template('user/edit_profile.html', form=form), 400
    
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    
    return render_template('user/edit_profile.html', form=form)
