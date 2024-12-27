from flask import Blueprint, render_template, redirect, url_for, request, current_app, flash, session
from app.models.user import User
from datetime import datetime
from app.models.audit_log import AuditLog
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
    form = UserForm()
    notification_count = get_notification_count(current_user.id)
    
    if form.validate_on_submit():
        try:
            # Validate unique fields
            if User.query.filter_by(username=form.username.data).first():
                raise ValueError("Username already exists")
            if User.query.filter_by(email=form.email.data).first():
                raise ValueError("Email already exists")
                
            # Create user
            new_user = create_user(form.data)
            
            # Create audit log with all required fields
            audit_log = AuditLog(
                user_id=current_user.id,
                action='create_user',
                object_type='User',
                object_id=new_user.id,
                details=f'Created user {new_user.username}',
                ip_address=request.remote_addr,
                timestamp=datetime.utcnow()
            )
            db.session.add(audit_log)
            db.session.commit()
            
            flash_message(FlashMessages.CREATE_USER_SUCCESS.value, FlashCategory.SUCCESS.value)
            return redirect(url_for('admin.user.index'))
        except ValueError as e:
            db.session.rollback()
            flash_message(str(e), FlashCategory.ERROR.value)
            
            # Log the failed attempt
            AuditLog.create(
                user_id=current_user.id,
                action='create_user_failed',
                details=f'Failed to create user: {str(e)}',
                ip_address=request.remote_addr
            )
            
            template = 'admin/users/_create_form.html' if request.headers.get('HX-Request') == 'true' else 'admin/users/create.html'
            return render_template(template, 
                                form=form,
                                notification_count=notification_count,
                                form_title='Create User'), 400
        except Exception as e:
            db.session.rollback()
            error_message = f"{FlashMessages.CREATE_USER_ERROR.value}: {str(e)}"
            # Log the error with audit details
            AuditLog.create(
                user_id=current_user.id,
                action='create_user_error',
                details=error_message,
                object_type='User',
                ip_address=request.remote_addr,
                details_before=str(form.data),
                details_after=None
            )
            flash_message(error_message, FlashCategory.ERROR.value)
            
            template = 'admin/users/_create_form.html' if request.headers.get('HX-Request') == 'true' else 'admin/users/create.html'
            
            flashed_messages = [(FlashCategory.ERROR.value, error_message)]
            
            return render_template(template, 
                                form=form, 
                                flash_messages=flashed_messages,
                                notification_count=notification_count), 400
    else:
        if request.headers.get('HX-Request') == 'true':
            return render_template('admin/users/_create_form.html', 
                                form=form,
                                notification_count=notification_count), 400
        else:
            error_messages = []
            field_errors = {}
            for field_name, errors in form.errors.items():
                field = getattr(form, field_name)
                field_errors[field_name] = []
                for error in errors:
                    msg = format_error_message(field, error)
                    error_messages.append(msg)
                    field_errors[field_name].append(msg)
                    flash_message(msg, FlashCategory.ERROR.value)
            flash_message(FlashMessages.CREATE_USER_INVALID_DATA.value, FlashCategory.ERROR.value)
    return render_template('admin/users/create.html', 
                         form=form,
                         notification_count=notification_count)
    
    # Create audit log entry
    audit_log = AuditLog(
        user_id=current_user.id,
        action='create_user',
        details_before='Creating new user',
        timestamp=datetime.utcnow(),
        ip_address=request.remote_addr
    )
    db.session.add(audit_log)
    db.session.commit()
    if form.validate_on_submit():
        try:
            new_user = create_user(form.data)
            flash(FlashMessages.CREATE_USER_SUCCESS.value, FlashCategory.SUCCESS.value)
            session.modified = True
            return redirect(url_for('admin.user.index'))
        except ValueError as e:
            db.session.rollback()
            flash_message(str(e), FlashCategory.ERROR.value)
            if request.headers.get('HX-Request') == 'true':
                return render_template('admin/users/_create_form.html', form=form), 400
            return render_template('admin/users/create.html', 
                                form=form,
                                notification_count=notification_count,
                                form_title='Create User'), 400
        except Exception as e:
            db.session.rollback()
            error_message = f"{FlashMessages.CREATE_USER_ERROR.value}: {str(e)}"
            flash_message(error_message, FlashCategory.ERROR.value)
            
            # For both HTMX and regular requests, render the appropriate template directly
            template = 'admin/users/_create_form.html' if request.headers.get('HX-Request') == 'true' else 'admin/users/create.html'
            
            # Get flashed messages and pass them explicitly to the template
            flashed_messages = [(FlashCategory.ERROR.value, error_message)]
            
            return render_template(template, 
                                form=form, 
                                flash_messages=flashed_messages), 400
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
                    flash_message(msg, FlashCategory.ERROR.value)
            flash_message(FlashMessages.CREATE_USER_INVALID_DATA.value, FlashCategory.ERROR.value)
    return render_template('admin/users/create.html', 
                         form=form,
                         notification_count=notification_count)

@admin_user_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
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
        
        if request.method == 'POST' and form.validate_on_submit():
            # Validate unique fields
            if user.username != form.username.data and User.query.filter_by(username=form.username.data).first():
                flash_message("Username already exists", FlashCategory.ERROR.value)
                return render_template('admin/users/edit.html', form=form), 400
                
            if user.email != form.email.data and User.query.filter_by(email=form.email.data).first():
                flash_message("Email already exists", FlashCategory.ERROR.value)
                return render_template('admin/users/edit.html', form=form), 400
                
            # Update user details
            try:
                update_user(user, form.data)
                
                # Create audit log
                AuditLog.create(
                    user_id=current_user.id,
                    action='update_user',
                    object_type='User',
                    object_id=user.id,
                    details=f'Updated user {user.username}',
                    ip_address=request.remote_addr
                )
                
                flash_message(FlashMessages.UPDATE_USER_SUCCESS.value, FlashCategory.SUCCESS.value)
                return redirect(url_for('admin.user.index'))
            except ValueError as e:
                db.session.rollback()
                logging.error(f"Validation error updating user {id}: {e}")
                flash_message(str(e), FlashCategory.ERROR.value)
            except Exception as e:
                db.session.rollback()
                logging.error(f"Failed to update user {id}: {e}")
                flash_message(f"{FlashMessages.UPDATE_USER_ERROR.value}: {str(e)}", FlashCategory.ERROR.value)
                
            db.session.commit()
    
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
@limiter.limit("3 per minute")
@login_required
@admin_required
def delete(id):
    """Delete a user with proper error handling and response codes"""
    try:
        user = get_user_by_id(id)
        
        # Prevent self-deletion
        if user.id == current_user.id:
            flash_message("Cannot delete your own account", FlashCategory.ERROR.value)
            return redirect(url_for('admin.user.index')), 400
            
        delete_user(user)
        
        # Audit log
        logging.info(f"User {current_user.id} deleted user {user.id} at {datetime.utcnow()}")
        
        flash_message(FlashMessages.DELETE_USER_SUCCESS.value, FlashCategory.SUCCESS.value)
        return redirect(url_for('admin.user.index')), 200
        
    except ValueError as e:
        flash_message(str(e), FlashCategory.ERROR.value)
        return redirect(url_for('admin.user.index')), 400
    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to delete user {id}: {e}")
        flash_message(f"{FlashMessages.DELETE_USER_ERROR.value}: {str(e)}", FlashCategory.ERROR.value)
        return redirect(url_for('admin.user.index')), 500

@admin_user_bp.route('/<int:id>/reset_password', methods=['POST'])
@limiter.limit("5 per hour")
@login_required
@admin_required
def reset_password(id):
    """Reset a user's password with audit logging"""
    try:
        user = get_user_by_id(id)
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
    """List users with search, pagination, and sorting"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search_query = request.args.get('q', '')
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        if search_query:
            # Handle sorting and pagination
            query = User.query
            if search_query:
                query = query.filter(User.username.ilike(f'%{search_query}%') | 
                                   User.email.ilike(f'%{search_query}%'))
        
            # Apply sorting
            if sort_by == 'username':
                query = query.order_by(User.username.asc() if sort_order == 'asc' else User.username.desc())
            elif sort_by == 'email':
                query = query.order_by(User.email.asc() if sort_order == 'asc' else User.email.desc())
            else:
                query = query.order_by(User.created_at.desc())
        
            # Apply pagination
            users = query.paginate(page=page, per_page=per_page, error_out=False)
        else:
            users = get_all_users(page=page, per_page=per_page, 
                                sort_by=sort_by, sort_order=sort_order)
        
        form = UserForm()
        return render_template('admin/users/index.html', 
                            users=users,
                            search_query=search_query,
                            form=form,
                            sort_by=sort_by,
                            sort_order=sort_order,
                            csrf_token=generate_csrf(),
                            _meta={'csrf': True})
    except Exception as e:
        logging.error(f"Error in user index route: {str(e)}")
        flash_message(FlashMessages.GENERIC_ERROR.value, FlashCategory.ERROR.value)
        return redirect(url_for('admin.dashboard.dashboard'))
