import logging
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from flask import request
from app.models.user import User
from app.models.notification import NotificationType
from app.models.audit_log import AuditLog
from app.models.notification import Notification
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

def create_user(form_data, current_user_id):
    """Create a new user with validation and audit logging"""
    try:
        # Validate unique fields
        if User.query.filter_by(username=form_data['username']).first():
            raise ValueError(FlashMessages.USERNAME_ALREADY_EXISTS.value)
        if User.query.filter_by(email=form_data['email']).first():
            raise ValueError(FlashMessages.EMAIL_ALREADY_EXISTS.value)
        
        # Create user
        new_user = User(
            username=form_data['username'],
            email=form_data['email'],
            is_admin=form_data.get('is_admin', False)
        )
        new_user.set_password(form_data['password'])
        
        db.session.add(new_user)
        db.session.commit()
        
        # Verify user creation
        if not new_user or not new_user.id:
            db.session.rollback()
            raise ValueError("Failed to create user - invalid user object returned")
        
        # Create audit log
        AuditLog.create(
            user_id=current_user_id,
            action='create_user',
            object_type='User',
            object_id=new_user.id,
            details=f'Created user {new_user.username}',
            ip_address=request.remote_addr
        )
        
        # Create notification with proper user_id
        Notification.create(
            type=NotificationType.CRUD_CREATE,
            message=f'User {new_user.username} was created',
            related_object=new_user,
            user_id=current_user_id
        )
        
        return new_user
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating user: {str(e)}")
        raise ValueError(f"{FlashMessages.CREATE_USER_ERROR.value}: {str(e)}")

def update_user(user, form_data):
    logger.info(f"Attempting to update user {user.id} with data: {form_data}")
    new_username = form_data['username']
    
    # Check for duplicate username
    if new_username != user.username:
        existing_user = User.query.filter_by(username=new_username).first()
        if existing_user:
            logger.warning(f"Username {new_username} already exists")
            raise ValueError(FlashMessages.USERNAME_ALREADY_EXISTS.value)
    
    user.username = new_username
    user.email = form_data['email']
    if 'password' in form_data and form_data['password']:
        user.set_password(form_data['password'])
    user.is_admin = form_data.get('is_admin', False)
    
    try:
        with db_session_scope() as session:
            session.add(user)
        logger.info(f"Successfully updated user {user.id}")
        flash_message(FlashMessages.PROFILE_UPDATE_SUCCESS, FlashCategory.SUCCESS)
    except Exception as e:
        logger.error(f"Failed to update user {user.id}: {str(e)}")
        flash_message(FlashMessages.PROFILE_UPDATE_FAILED, FlashCategory.ERROR)
        raise ValueError(f"Failed to update user: {str(e)}")
