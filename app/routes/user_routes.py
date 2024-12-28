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
        if not form.validate():
            if 'csrf_token' in form.errors:
                flash_message(FlashMessages.CSRF_INVALID, FlashCategory.ERROR)
                return render_template('user/edit_profile.html', form=form), 400
            
            # Ensure CSRF token is present and valid
            if not form.csrf_token.data:
                flash_message(FlashMessages.CSRF_INVALID, FlashCategory.ERROR)
                return render_template('user/edit_profile.html', form=form), 400
                
            # Handle specific validation errors
            if 'username' in form.errors:
                for error in form.username.errors:
                    if error == FlashMessages.USERNAME_ALREADY_EXISTS.value:
                        flash_message(FlashMessages.USERNAME_ALREADY_EXISTS, FlashCategory.ERROR)
                    else:
                        flash_message(FlashMessages.PROFILE_UPDATE_INVALID_DATA, FlashCategory.ERROR)
            elif 'email' in form.errors:
                for error in form.email.errors:
                    if error == FlashMessages.EMAIL_ALREADY_EXISTS.value:
                        flash_message(FlashMessages.EMAIL_ALREADY_EXISTS, FlashCategory.ERROR)
                    else:
                        flash_message(FlashMessages.PROFILE_UPDATE_INVALID_DATA, FlashCategory.ERROR)
            else:
                flash_message(FlashMessages.PROFILE_UPDATE_INVALID_DATA, FlashCategory.ERROR)
                
            return render_template('user/edit_profile.html', form=form), 400
            
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
    
    return render_template('user/edit_profile.html', form=form)
