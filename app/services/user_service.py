import logging
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from flask import request
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

def get_all_users(page=1, per_page=10, sort_by='created_at', sort_order='desc'):
    """Get paginated list of users with sorting options.
    
    Args:
        page: Page number (1-based)
        per_page: Items per page
        sort_by: Field to sort by ('username', 'email', or 'created_at')
        sort_order: Sort direction ('asc' or 'desc')
    
    Returns:
        Pagination object with users
    """
    query = User.query
    
    # Validate and apply sorting
    if sort_by == 'username':
        query = query.order_by(User.username.asc() if sort_order == 'asc' else User.username.desc())
    elif sort_by == 'email':
        query = query.order_by(User.email.asc() if sort_order == 'asc' else User.email.desc())
    else:  # Default to created_at
        query = query.order_by(User.created_at.desc())
    
    return query.paginate(page=page, per_page=per_page)

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
    try:
        username = form_data['username']
        email = form_data['email']
        password = form_data['password']
        is_admin = form_data.get('is_admin', False)
        
        # Detailed audit logging
        audit_details = {
            'username': username,
            'email': email,
            'is_admin': is_admin,
            'created_by': current_user.username
        }

        # Validate password strength
        if not validate_password_strength(password):
            raise ValueError(FlashMessages.PASSWORD_WEAK.value)

        # Check for existing user
        if User.query.filter_by(username=username).first():
            raise ValueError(FlashMessages.USERNAME_ALREADY_EXISTS.value)
        if User.query.filter_by(email=email).first():
            raise ValueError(FlashMessages.EMAIL_ALREADY_EXISTS.value)

        new_user = User(username=username, email=email, is_admin=is_admin)
        new_user.set_password(password)
        
        # Create audit log
        AuditLog.create(
            user_id=current_user.id,
            action='create_user',
            object_type='User',
            object_id=new_user.id,
            details=f'Created user {username}',
            ip_address=request.remote_addr
        )
        
        db.session.add(new_user)
        db.session.commit()
        return new_user
        
    except IntegrityError as e:
        db.session.rollback()
        raise ValueError(f"{FlashMessages.USERNAME_ALREADY_EXISTS.value}: {str(e)}")
    except Exception as e:
        db.session.rollback()
        raise ValueError(f"{FlashMessages.CREATE_USER_ERROR.value}: {str(e)}")

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
