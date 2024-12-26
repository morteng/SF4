from flask import Blueprint, render_template, redirect, url_for, request, current_app, flash
from flask_login import login_required, current_user
from app.constants import FLASH_MESSAGES, FLASH_CATEGORY_SUCCESS, FLASH_CATEGORY_ERROR
from app.forms.admin_forms import UserForm
from app.forms.user_forms import ProfileForm
from app.services.user_service import get_user_by_id, delete_user, get_all_users, create_user, update_user
from app.utils import admin_required, flash_message, format_error_message
import logging
from app.extensions import db  # Import the db object

admin_user_bp = Blueprint('user', __name__, url_prefix='/users')

@admin_user_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    form = UserForm()
    if form.validate_on_submit():
        try:
            new_user = create_user(form.data)
            flash_message(FLASH_MESSAGES["CREATE_USER_SUCCESS"], FLASH_CATEGORY_SUCCESS)
            return redirect(url_for('admin.user.index'))
        except Exception as e:
            db.session.rollback()  # Ensure the session is rolled back on error
            flash_message(f"{FLASH_MESSAGES['CREATE_USER_ERROR']} {str(e)}", FLASH_CATEGORY_ERROR)
    else:
        if request.headers.get('HX-Request') == 'true':
            # HTMX response - return form with errors
            return render_template('admin/users/_create_form.html', form=form), 400
        else:
            # Regular form submission
            error_messages = []
            field_errors = {}
            for field_name, errors in form.errors.items():
                field = getattr(form, field_name)
                field_errors[field_name] = []
                for error in errors:
                    msg = format_error_message(field, error)
                    error_messages.append(msg)
                    field_errors[field_name].append(msg)
                    flash_message(msg, FLASH_CATEGORY_ERROR)
            if not form.validate_on_submit():
                flash_message(FLASH_MESSAGES["CREATE_USER_INVALID_DATA"], FLASH_CATEGORY_ERROR)
    return render_template('admin/users/create.html', form=form)

@admin_user_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    user = get_user_by_id(id)
    if not user:
        flash_message(FLASH_MESSAGES["USER_NOT_FOUND"], FLASH_CATEGORY_ERROR)  # Use specific user not found message
        return redirect(url_for('admin.user.index'))
    
    form = UserForm(
        original_username=user.username,
        original_email=user.email,
        obj=user
    )
    if request.method == 'POST' and form.validate_on_submit():
        try:
            update_user(user, form.data)
            flash_message(FLASH_MESSAGES["UPDATE_USER_SUCCESS"], FLASH_CATEGORY_SUCCESS)
            return redirect(url_for('admin.user.index'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Failed to update user {id}: {e}")
            flash_message(f"{FLASH_MESSAGES['UPDATE_USER_ERROR']} {str(e)}", FLASH_CATEGORY_ERROR)
    
    return render_template('admin/users/_edit_row.html', form=form, user=user)

@admin_user_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(id):
    user = get_user_by_id(id)
    if not user:
        flash_message(FLASH_MESSAGES["USER_NOT_FOUND"], FLASH_CATEGORY_ERROR)  # Use specific user not found message
        return redirect(url_for('admin.user.index'))
    
    try:
        delete_user(user)
        flash_message(FLASH_MESSAGES["DELETE_USER_SUCCESS"], FLASH_CATEGORY_SUCCESS)
    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to delete user {id}: {e}")
        flash_message(f"{FLASH_MESSAGES['DELETE_USER_ERROR']} {str(e)}", FLASH_CATEGORY_ERROR)
    
    return redirect(url_for('admin.user.index'))

@admin_user_bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile():
    form = ProfileForm(
        original_username=current_user.username,
        original_email=current_user.email,
        obj=current_user
    )
    if request.method == 'POST' and form.validate_on_submit():
        try:
            update_user(current_user, form.data)
            flash_message(FLASH_MESSAGES["PROFILE_UPDATE_SUCCESS"], FLASH_CATEGORY_SUCCESS)
            return redirect(url_for('admin.user.index'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Failed to update user {current_user.id}: {e}")
            flash_message(f"{FLASH_MESSAGES['PROFILE_UPDATE_ERROR']} {str(e)}", FLASH_CATEGORY_ERROR)
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash_message(error, FLASH_CATEGORY_ERROR)  # Flash each error message using flash_message
    return render_template('admin/users/edit_profile.html', form=form)

@admin_user_bp.route('/', methods=['GET'])
@login_required
@admin_required
def index():
    users = get_all_users()
    return render_template('admin/users/index.html', users=users)
