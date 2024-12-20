from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required
from app.constants import FLASH_MESSAGES, FLASH_CATEGORY_SUCCESS, FLASH_CATEGORY_ERROR
from app.forms.admin_forms import UserForm
from app.services.user_service import get_user_by_id, delete_user, get_all_users, create_user, update_user
from app.utils import admin_required
import logging

admin_user_bp = Blueprint('user', __name__, url_prefix='/users')

@admin_user_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    form = UserForm()
    if form.validate_on_submit():
        try:
            new_user = create_user(form.data)
            flash(FLASH_MESSAGES["CREATE_USER_SUCCESS"], FLASH_CATEGORY_SUCCESS)
            return redirect(url_for('admin.user.index'))
        except Exception as e:
            db.session.rollback()  # Ensure the session is rolled back on error
            flash(f"{FLASH_MESSAGES['CREATE_USER_ERROR']}{str(e)}", FLASH_CATEGORY_ERROR)
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", FLASH_CATEGORY_ERROR)
        flash(FLASH_MESSAGES["CREATE_USER_ERROR"], FLASH_CATEGORY_ERROR)  # Add this line to set a generic creation error message
    return render_template('admin/users/create.html', form=form)

@admin_user_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    user = get_user_by_id(id)
    if not user:
        flash(FLASH_MESSAGES["GENERIC_ERROR"], FLASH_CATEGORY_ERROR)
        return redirect(url_for('admin.user.index'))
    
    form = UserForm(
        original_username=user.username,
        original_email=user.email,
        obj=user
    )
    if request.method == 'POST' and form.validate_on_submit():
        try:
            update_user(user, form.data)
            flash(FLASH_MESSAGES["UPDATE_USER_SUCCESS"], FLASH_CATEGORY_SUCCESS)
            return redirect(url_for('admin.user.index'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Failed to update user {id}: {e}")
            flash(f"{FLASH_MESSAGES['UPDATE_USER_ERROR']}{str(e)}", FLASH_CATEGORY_ERROR)
    
    return render_template('admin/users/_edit_row.html', form=form, user=user)

@admin_user_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(id):
    user = get_user_by_id(id)
    if not user:
        flash(FLASH_MESSAGES["GENERIC_ERROR"], FLASH_CATEGORY_ERROR)
        return redirect(url_for('admin.user.index'))
    
    try:
        delete_user(user)
        flash(FLASH_MESSAGES["DELETE_USER_SUCCESS"], FLASH_CATEGORY_SUCCESS)
    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to delete user {id}: {e}")
        flash(f"{FLASH_MESSAGES['DELETE_USER_ERROR']}{str(e)}", FLASH_CATEGORY_ERROR)
    
    return redirect(url_for('admin.user.index'))

@admin_user_bp.route('/', methods=['GET'])
@login_required
@admin_required
def index():
    users = get_all_users()
    return render_template('admin/users/index.html', users=users)
