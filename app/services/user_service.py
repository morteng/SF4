import logging
from app.utils import db_session_scope

logger = logging.getLogger(__name__)
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from flask import request
from app.models.user import User
from app.models.notification import NotificationType
from app.models.audit_log import AuditLog
from app.models.notification import Notification
from app.extensions import db
from app.utils import flash_message
from app.constants import FlashMessages, FlashCategory
from flask_login import current_user

def get_user_by_id(user_id):
    """Get user by ID with proper validation and error handling"""
    if not user_id or not isinstance(user_id, int):
        raise ValueError("Invalid user ID")
        
    try:
        user = db.session.get(User, user_id)
        if not user:
            raise ValueError(FlashMessages.USER_NOT_FOUND.value)
        return user
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {str(e)}")
        raise ValueError(f"Error retrieving user: {str(e)}")

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

def validate_password_strength(password):
    """Validate password strength with detailed error messages"""
    if len(password) < 12:
        return False, "Password must be at least 12 characters long"
    
    has_upper = any(char.isupper() for char in password)
    has_lower = any(char.islower() for char in password)
    has_digit = any(char.isdigit() for char in password)
    has_special = any(not char.isalnum() for char in password)
    
    if not all([has_upper, has_lower, has_digit, has_special]):
        return False, "Password must contain uppercase, lowercase, numbers and special characters"
    
    return True, ""

def create_user(form_data, current_user_id=None):
    """Create a new user with validation and audit logging"""
    logger = logging.getLogger(__name__)
    try:
        logger.info(f"Attempting to create user: {form_data['username']}")
        
        # Validate unique fields
        if User.query.filter_by(username=form_data['username']).first():
            logger.warning(f"Username already exists: {form_data['username']}")
            raise ValueError(FlashMessages.USERNAME_ALREADY_EXISTS.value)
        if User.query.filter_by(email=form_data['email']).first():
            logger.warning(f"Email already exists: {form_data['email']}")
            raise ValueError(FlashMessages.EMAIL_ALREADY_EXISTS.value)
        
        # Validate password strength for admin users
        if form_data.get('is_admin', False):
            is_valid, message = validate_password_strength(form_data['password'])
            if not is_valid:
                raise ValueError(f"Admin password requirements: {message}")
        
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
            logger.error("Failed to create user - invalid user object returned")
            db.session.rollback()
            raise ValueError("Failed to create user - invalid user object returned")
        
        logger.info(f"Successfully created user: {new_user.username} (ID: {new_user.id})")
        
        # Create audit log
        AuditLog.create(
            user_id=current_user_id if current_user_id else 0,  # 0 = system
            action='create_user',
            object_type='User',
            object_id=new_user.id,
            details=f'Created user {new_user.username}',
            ip_address=request.remote_addr
        )
        
        # Create notification
        Notification.create(
            type=NotificationType.CRUD_CREATE,
            message=f'User {new_user.username} was created',
            related_object=new_user,
            user_id=current_user_id if current_user_id else 0  # 0 = system
        )
        
        return new_user
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}", exc_info=True)
        db.session.rollback()
        raise ValueError(f"{FlashMessages.CREATE_USER_ERROR.value}: {str(e)}")

def update_user(user, form_data):
    logger = logging.getLogger(__name__)
    try:
        logger.info(f"Attempting to update user {user.id} with data: {form_data}")
        
        # Validate input
        if not user or not form_data:
            raise ValueError("Invalid user or form data")
            
        # Check for duplicate username
        new_username = form_data.get('username')
        if new_username and new_username != user.username:
            existing_user = User.query.filter_by(username=new_username).first()
            if existing_user:
                logger.warning(f"Username {new_username} already exists")
                raise ValueError(FlashMessages.USERNAME_ALREADY_EXISTS.value)
        
        # Update user fields
        user.username = form_data.get('username', user.username)
        user.email = form_data.get('email', user.email)
        if 'password' in form_data and form_data['password']:
            user.set_password(form_data['password'])
        user.is_admin = form_data.get('is_admin', user.is_admin)
        
        db.session.commit()
        logger.info(f"Successfully updated user {user.id}")
        return user
        
    except Exception as e:
        logger.error(f"Failed to update user {user.id if user else 'unknown'}: {str(e)}")
        db.session.rollback()
        raise ValueError(f"Failed to update user: {str(e)}")
