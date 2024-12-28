from flask import Blueprint, render_template, redirect, url_for, request, current_app, flash, session
from werkzeug.security import generate_password_hash
from app.models.user import User
from datetime import datetime
from app.models.audit_log import AuditLog
from app.models.notification import Notification
from app.services.notification_service import get_notification_count
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import generate_csrf
from app.utils import generate_temp_password
from flask_login import login_required, current_user
from app.constants import FlashMessages, FlashCategory
from app.forms.admin_forms import UserForm
from app.forms.user_forms import ProfileForm
from app.services.user_service import get_user_by_id, delete_user, get_all_users, create_user, update_user, search_users
from app.utils import admin_required, flash_message, format_error_message
import logging
from datetime import datetime
from app.extensions import db  # Import the db object

admin_user_bp = Blueprint('user', __name__, url_prefix='/users')

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]  # Default fallback values
)

@admin_user_bp.route('/create', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
@login_required
@admin_required
def create():
    """Create a new user with proper validation and audit logging"""
    # Safety check for current_user
    if not hasattr(current_user, 'id'):
        flash_message("User not properly authenticated", FlashCategory.ERROR)
        return redirect(url_for('public.login'))
        
    form = UserForm()
    notification_count = get_notification_count(current_user.id)
    
    if request.method == 'GET':
        return render_template('admin/users/create.html', 
                            form=form,
                            notification_count=notification_count)
    
    if form.validate_on_submit():
        try:
            # Prepare user data
            user_data = {
                'username': form.username.data,
                'email': form.email.data,
                'password': form.password.data,
                'is_admin': form.is_admin.data if hasattr(form, 'is_admin') else False
            }

            # Create user through service layer
            new_user = create_user(user_data, current_user.id)
            
            # Verify user creation
            if not new_user or not new_user.id:
                db.session.rollback()
                raise ValueError("Failed to create user - invalid user object returned")
                
                # Create audit log with before/after state
                AuditLog.create(
                    user_id=current_user.id,
                    action=FlashMessages.AUDIT_CREATE.value,
                    object_type='User',
                    object_id=new_user.id,
                    details_before=None,
                    details_after={
                        'username': new_user.username,
                        'email': new_user.email,
                        'is_admin': new_user.is_admin
                    },
                    ip_address=request.remote_addr
                )
                
                # Create notification with proper type and message
                Notification.create(
                    type='user_created',
                    message=FlashMessages.USER_CREATED.value.format(username=new_user.username),
                    related_object=f'User:{new_user.id}',
                    user_id=current_user.id
                )
                
                flash_message(FlashMessages.CREATE_USER_SUCCESS.value, FlashCategory.SUCCESS)
                return redirect(url_for('admin.user.index'))
                
        except ValueError as e:
            # Handle validation errors
            db.session.rollback()
            logging.error(f"Validation error creating user: {str(e)}")
            flash_message(str(e), FlashCategory.ERROR)
            return render_template('admin/users/create.html',
                                form=form,
                                notification_count=notification_count), 400
        except Exception as e:
            # Handle other errors
            db.session.rollback()
            logging.error(f"Error creating user: {str(e)}")
            flash_message(f"{FlashMessages.CREATE_USER_ERROR.value}: {str(e)}", FlashCategory.ERROR)
            return render_template('admin/users/create.html',
                                form=form,
                                notification_count=notification_count), 500

    # Handle form validation errors
    error_messages = []
    for field_name, errors in form.errors.items():
        field = getattr(form, field_name)
        for error in errors:
            msg = format_error_message(field, error)
            error_messages.append(msg)
            flash_message(msg, FlashCategory.ERROR)
            
    return render_template('admin/users/create.html', 
                        form=form,
                        notification_count=notification_count), 400

@admin_user_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@limiter.limit("10 per minute")  # Matches project rate limiting specs
@login_required
@admin_required
def edit(id):
    """Edit user details with proper validation and audit logging"""
    """Edit user with audit logging and validation"""
    """Edit user details with proper validation and audit logging"""
    try:
        user = get_user_by_id(id)
        if not user:
            flash_message(FlashMessages.USER_NOT_FOUND.value, FlashCategory.ERROR.value)
            return redirect(url_for('admin.user.index'))
            
        form = UserForm(
            original_username=user.username,
            original_email=user.email,
            obj=user
        )
        
        if request.method == 'GET':
            csrf_token = generate_csrf()
            return render_template('admin/users/edit.html', 
                                form=form,
                                user=user,
                                csrf_token=csrf_token)
            
        form = UserForm(
            original_username=user.username,
            original_email=user.email,
            obj=user
        )
        
        if request.method == 'POST' and form.validate_on_submit():
            # Validate unique fields
            if user.username != form.username.data and User.query.filter_by(username=form.username.data).first():
                flash_message(FlashMessages.USERNAME_ALREADY_EXISTS.value, FlashCategory.ERROR.value)
                return render_template('admin/users/edit.html', form=form, user=user), 400
                
            if user.email != form.email.data and User.query.filter_by(email=form.email.data).first():
                flash_message(FlashMessages.EMAIL_ALREADY_EXISTS.value, FlashCategory.ERROR.value)
                return render_template('admin/users/edit.html', form=form, user=user), 400
                
            # Update user details
            try:
                old_username = user.username
                update_user(user, form.data)
                
                # Create audit log with both old and new username
                AuditLog.create(
                    user_id=current_user.id,
                    action='update_user',
                    object_type='User',
                    object_id=user.id,
                    details=f'Updated username from {old_username} to {user.username}',
                    ip_address=request.remote_addr
                )
                
                flash_message(FlashMessages.UPDATE_USER_SUCCESS.value, FlashCategory.SUCCESS.value)
                return redirect(url_for('admin.user.index'))
            except ValueError as e:
                db.session.rollback()
                logging.error(f"Validation error updating user {id}: {e}")
                flash_message(str(e), FlashCategory.ERROR.value)
                return render_template('admin/users/edit.html', form=form, user=user), 400
            except Exception as e:
                db.session.rollback()
                logging.error(f"Failed to update user {id}: {e}")
                flash_message(f"{FlashMessages.UPDATE_USER_ERROR.value}: {str(e)}", FlashCategory.ERROR.value)
                return render_template('admin/users/edit.html', form=form, user=user), 500
    
        return render_template('admin/users/edit.html', 
                         form=form,
                         user=user)
    except ValueError as e:
        flash_message(str(e), FlashCategory.ERROR.value)
        return redirect(url_for('admin.user.index'))
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error in edit route for user {id}: {e}")
        flash_message(f"An unexpected error occurred: {str(e)}", FlashCategory.ERROR.value)
        return redirect(url_for('admin.user.index')), 500

@admin_user_bp.route('/<int:id>/delete', methods=['POST'])
@limiter.limit("3 per minute")  # Matches project rate limiting specs
@login_required
@admin_required
@login_required
@admin_required
def delete(id):
    """Delete a user with proper error handling and response codes"""
    user = get_user_by_id(id)
    
    # Prevent self-deletion
    if user.id == current_user.id:
        flash_message("Cannot delete your own account", FlashCategory.ERROR.value)
        return redirect(url_for('admin.user.index')), 400
        
    try:
        try:
            username = user.username
            delete_user(user)
                
            # Create audit log with captured username
            AuditLog.create(
                user_id=current_user.id,
                action='delete_user',
                object_type='User',
                object_id=user.id,
                details=f'Deleted user {username}',
                ip_address=request.remote_addr
            )
                
            # Create notification
            Notification.create(
                type='user_deleted',
                message=f'User {username} was deleted',
                related_object=f'User:{user.id}'
            )
            
            # Audit log
            logging.info(f"User {current_user.id} deleted user {user.id} at {datetime.utcnow()}")
            
            flash_message(FlashMessages.DELETE_USER_SUCCESS.value, FlashCategory.SUCCESS.value)
            return redirect(url_for('admin.user.index'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Failed to delete user {id}: {e}")
            flash_message(f"{FlashMessages.DELETE_USER_ERROR.value}: {str(e)}", FlashCategory.ERROR.value)
            return redirect(url_for('admin.user.index'))
        
    except ValueError as e:
        flash_message(str(e), FlashCategory.ERROR.value)
        return redirect(url_for('admin.user.index')), 400
    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to delete user {id}: {e}")
        flash_message(f"{FlashMessages.DELETE_USER_ERROR.value}: {str(e)}", FlashCategory.ERROR.value)
        return redirect(url_for('admin.user.index')), 500
    finally:
        db.session.close()

@admin_user_bp.route('/<int:id>/reset_password', methods=['POST'])
@limiter.limit("5 per hour")  # Matches project rate limiting specs
@login_required
@admin_required
@login_required
@admin_required
def reset_password(id):
    """Reset a user's password with audit logging"""
    try:
        user = get_user_by_id(id)
        if not user:
            flash_message(FlashMessages.USER_NOT_FOUND.value, FlashCategory.ERROR.value)
            return redirect(url_for('admin.user.index')), 404
            
        temp_password = generate_temp_password()
        user.set_password(temp_password)
        
        # Create audit log
        AuditLog.create(
            user_id=current_user.id,
            action='reset_password',
            object_type='User',
            object_id=user.id,
            details=f'Reset password for user {user.username}',
            ip_address=request.remote_addr
        )
        
        db.session.commit()
        
        # TODO: Send email with temporary password
        logging.info(f"Password reset for user {user.id} by admin {current_user.id}")
        
        flash_message(FlashMessages.PASSWORD_RESET_SUCCESS.value, FlashCategory.SUCCESS.value)
        return redirect(url_for('admin.user.index')), 200
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to reset password for user {id}: {e}")
        flash_message(f"{FlashMessages.PASSWORD_RESET_ERROR.value}: {str(e)}", FlashCategory.ERROR.value)
        return redirect(url_for('admin.user.index')), 500

@admin_user_bp.route('/<int:id>/toggle_active', methods=['POST'])
@limiter.limit("10 per hour")
@login_required
@admin_required
def toggle_active(id):
    """Activate/Deactivate a user"""
    try:
        user = get_user_by_id(id)
        
        # Prevent self-deactivation
        if user.id == current_user.id:
            flash_message("Cannot deactivate your own account", FlashCategory.ERROR.value)
            return redirect(url_for('admin.user.index')), 400
            
        user.is_active = not user.is_active
        db.session.commit()
        
        message = FlashMessages.USER_ACTIVATED.value if user.is_active else FlashMessages.USER_DEACTIVATED.value
        flash_message(message, FlashCategory.SUCCESS.value)
        return redirect(url_for('admin.user.index')), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to toggle active status for user {id}: {e}")
        flash_message("Failed to update user status", FlashCategory.ERROR.value)
        return redirect(url_for('admin.user.index')), 500

@admin_user_bp.route('/edit_profile', methods=['GET', 'POST'])
@limiter.limit("10 per minute")  # Rate limit for profile edits
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
            flash_message(FlashMessages.PROFILE_UPDATE_SUCCESS.value, FlashCategory.SUCCESS.value)
            return redirect(url_for('admin.user.index'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Failed to update user {current_user.id}: {e}")
            flash_message(f"{FlashMessages.PROFILE_UPDATE_ERROR.value} {str(e)}", FlashCategory.ERROR.value)
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash_message(error, FlashCategory.ERROR.value)  # Flash each error message using flash_message
    return render_template('admin/users/edit_profile.html', form=form)

@admin_user_bp.route('/', methods=['GET'])
@login_required
@admin_required
def index():
    """List users with pagination and search"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search_query = request.args.get('q', '')
    
    if search_query:
        users = search_users(search_query, page=page, per_page=per_page)
    else:
        users = get_all_users(page=page, per_page=per_page)
    
    return render_template('admin/users/index.html', 
                         users=users,
                         search_query=search_query,
                         csrf_token=generate_csrf())
