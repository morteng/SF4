import logging
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.models.audit_log import AuditLog
from app.extensions import db
from app.utils import flash_message, validate_password_strength
from app.constants import FlashMessages, FlashCategory
from flask_login import current_user

def get_user_by_id(user_id):
    """Get user by ID with error handling"""
    user = db.session.get(User, user_id)
    if not user:
        raise ValueError(FlashMessages.USER_NOT_FOUND.value)
    return user

def delete_user(user):
    """Delete user with proper error handling and logging"""
    if not user:
        raise ValueError(FlashMessages.USER_NOT_FOUND.value)
    
    try:
        db.session.delete(user)
        db.session.commit()
        logging.info(f"User {user.id} deleted successfully")
    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to delete user {user.id}: {str(e)}")
        raise ValueError(f"{FlashMessages.DELETE_USER_ERROR.value}: {str(e)}")

from sqlalchemy import or_

def get_all_users(page=1, per_page=10):
    return User.query.paginate(page=page, per_page=per_page)

def search_users(query, page=1, per_page=10):
    """Search users with error handling"""
    try:
        return User.query.filter(
            or_(
                User.username.ilike(f'%{query}%'),
                User.email.ilike(f'%{query}%')
            )
        ).paginate(page=page, per_page=per_page)
    except Exception as e:
        logging.error(f"Error searching users: {str(e)}")
        raise ValueError(FlashMessages.USER_SEARCH_ERROR.value)

def create_user(form_data):
    """Create a new user with validation and audit logging"""
    username = form_data['username']
    email = form_data['email']
    password = form_data['password']
    is_admin = form_data.get('is_admin', False)

    # Validate password strength
    if not validate_password_strength(password):
        raise ValueError(FlashMessages.PASSWORD_WEAK.value)

    new_user = User(username=username, email=email, is_admin=is_admin)
    new_user.set_password(password)
    
    # Audit log - ensure we use the admin user's ID
    if current_user and current_user.is_authenticated:
        audit_log = AuditLog(
            user_id=current_user.id,  # Use the admin user's ID
            action='create_user',
            details_before=f'Creating user: {username}',
            timestamp=datetime.utcnow()
        )
        db.session.add(audit_log)
    
    try:
        db.session.add(new_user)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        raise ValueError(f"{FlashMessages.USERNAME_ALREADY_EXISTS.value}: {str(e)}")
    except Exception as e:
        db.session.rollback()
        raise ValueError(f"{FlashMessages.CREATE_USER_ERROR.value}{str(e)}")
    
    return new_user

def update_user(user, form_data):
    print(f"Updating user with data: {form_data}")  # Debug statement
    new_username = form_data['username']
    
    # Check for duplicate username
    if new_username != user.username:
        existing_user = User.query.filter_by(username=new_username).first()
        if existing_user:
            raise ValueError(FlashMessages.USERNAME_ALREADY_EXISTS.value)
    
    user.username = new_username
    user.email = form_data['email']
    if 'password' in form_data and form_data['password']:
        user.set_password(form_data['password'])
    user.is_admin = form_data.get('is_admin', False)
    
    try:
        db.session.commit()
        flash_message(FlashMessages.PROFILE_UPDATE_SUCCESS, FlashCategory.SUCCESS)
        print(f"User {user.username} updated successfully.")  # Debug statement
    except Exception as e:
        flash_message(FlashMessages.PROFILE_UPDATE_FAILED, FlashCategory.ERROR)
        print(f"Failed to update user: {e}")  # Debug statement
        db.session.rollback()
        raise ValueError("Failed to update user.")
