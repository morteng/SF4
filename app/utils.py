# app/utils.py
import os
import logging
import string
import secrets
import json
from datetime import datetime, timezone
from typing import Any, Union
from flask import abort, redirect, url_for, flash, request, current_app, render_template
from app.models.notification import Notification
from flask_wtf.csrf import generate_csrf
from app.models.audit_log import AuditLog
from app.constants import FlashMessages, FlashCategory
from app.extensions import db  

def generate_csrf_token():
    """Generate a CSRF token for form validation."""
    return generate_csrf()

# Configure logging
logger = logging.getLogger(__name__)
from flask_login import current_user, login_required as _login_required  # Import the original login_required
from .models.user import User
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv  
from app.extensions import db  
from app.models.audit_log import AuditLog  
from app.models.notification import Notification  

from functools import wraps
from datetime import datetime

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash_message(FlashMessages.LOGIN_REQUIRED.value, FlashCategory.ERROR.value)
            return redirect(url_for('public.login'))
            
        if not current_user.is_admin:
            # Create audit log for unauthorized access attempt
            with current_app.app_context():
                try:
                    audit_log = AuditLog(
                        user_id=current_user.id if current_user.is_authenticated else None,
                        action='unauthorized_access',
                        object_type='AdminPanel',
                        details=f'Attempted access to {request.path}',
                        ip_address=request.remote_addr,
                        http_method=request.method,
                        endpoint=request.endpoint
                    )
                    db.session.add(audit_log)
                    db.session.commit()
                except Exception as e:
                    current_app.logger.error(f"Error creating audit log: {str(e)}")
                    db.session.rollback()
                
                try:
                    notification = Notification(
                        type='security',
                        message=f'Unauthorized access attempt to {request.path}',
                        user_id=current_user.id
                    )
                    db.session.add(notification)
                    db.session.commit()
                except Exception as e:
                    current_app.logger.error(f"Error creating notification: {str(e)}")
                    db.session.rollback()
                
            flash_message(FlashMessages.ADMIN_ACCESS_DENIED.value, FlashCategory.ERROR.value)
            return abort(403)
            
        # Create single audit log for admin access
        with current_app.app_context():
            try:
                audit_log = AuditLog(
                    user_id=current_user.id,
                    action=f.__name__,
                    details=f"Accessed admin route: {request.path}",
                    ip_address=request.remote_addr,
                    http_method=request.method,
                    endpoint=request.endpoint
                )
                db.session.add(audit_log)
                db.session.commit()
            except Exception as e:
                current_app.logger.error(f"Error creating audit log: {str(e)}")
                db.session.rollback()
            
        if not current_user.is_admin:
            flash_message(FlashMessages.ADMIN_REQUIRED.value, FlashCategory.ERROR.value)
            return abort(403)
            
        try:
            # Add audit log
            audit_log = AuditLog(
                user_id=current_user.id,
                action=f.__name__,
                details_before=f"Accessed admin route: {request.path}",
                timestamp=datetime.now(timezone.utc)
            )
            db.session.add(audit_log)
            db.session.commit()
        except Exception as e:
            logger.error(f"Error creating audit log: {str(e)}")
            
        return f(*args, **kwargs)
    return decorated_function

# Define login_required in utils.py
login_required = _login_required

def init_admin_user() -> None:
    """
    Initialize the admin user from environment variables.
    
    Raises:
        RuntimeError: If required environment variables are missing
    """
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Initializing admin user")
        load_dotenv()  # Load environment variables from .env file
        username = os.environ.get('ADMIN_USERNAME')
        password = os.environ.get('ADMIN_PASSWORD')
        email = os.environ.get('ADMIN_EMAIL')

        if not all([username, password, email]):
            raise RuntimeError("Missing required environment variables for admin user")

        if not User.query.filter_by(username=username).first():
            admin_user = User(
                username=username,
                password_hash=generate_password_hash(password),
                email=email,
                is_admin=True
            )
            db.session.add(admin_user)
            db.session.commit()
            logger.info("Admin user initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing admin user: {str(e)}")
        raise RuntimeError(f"Failed to initialize admin user: {str(e)}")

from urllib.parse import urlparse
import re
from itsdangerous import URLSafeTimedSerializer
from flask import current_app

def decode_csrf_token(encoded_token):
    """Decode a CSRF token from its encoded form.
    
    Args:
        encoded_token: The encoded CSRF token from the form
        
    Returns:
        str: The decoded raw CSRF token
        
    Raises:
        BadSignature: If the token is invalid or tampered with
    """
    # Create a serializer with the same configuration as Flask-WTF
    serializer = URLSafeTimedSerializer(
        current_app.config['SECRET_KEY'],
        salt='csrf-token'
    )
    
    try:
        # Load the token to get the raw value
        return serializer.loads(encoded_token, max_age=None)
    except Exception as e:
        # Log the error for debugging
        logger.error(f"Failed to decode CSRF token: {str(e)}")
        raise

import re
from typing import Tuple

def validate_password_strength(password: str) -> bool:
    """Validate password strength according to project requirements.
    
    Args:
        password: Password to validate
        
    Returns:
        bool: True if password meets strength requirements
    """
    # Minimum 8 characters
    if len(password) < 8:
        return False
    
    # At least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False
    
    # At least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False
    
    # At least one number
    if not re.search(r'[0-9]', password):
        return False
    
    # At least one special character
    if not re.search(r'[^A-Za-z0-9]', password):
        return False
    
    # Check against common passwords
    common_passwords = ['password', '123456', 'qwerty']
    if password.lower() in common_passwords:
        return False
        
    return True

def get_unread_notification_count() -> int:
    """Get count of unread notifications"""
    from app.models.notification import Notification
    return Notification.query.filter_by(read_status=False).count()

def generate_temp_password(length: int = 12) -> str:
    """Generate a temporary password with the specified length.
    
    Args:
        length: Length of the password to generate
        
    Returns:
        str: Generated temporary password
    """
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(chars) for _ in range(length))

def validate_url(url: str) -> bool:
    """
    Validate URL format according to RFC standards.
    
    Args:
        url: URL string to validate
        
    Returns:
        bool: True if URL is valid, False otherwise
        
    Raises:
        ValueError: If URL parsing fails
        
    Validation Rules:
        - Must start with http:// or https://
        - Must have valid scheme and netloc
        - Must be properly formatted according to URL standards
        
    Example:
        >>> validate_url("https://example.com")
        True
        >>> validate_url("invalid_url")
        False
    """
    try:
        if not url:
            logger.warning("Empty URL provided for validation.")
            return False
        
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            logger.warning(f"Invalid URL format: {url}")
            return False
        
        if not re.match(r'^https?://', url):
            logger.warning(f"URL must start with http:// or https://: {url}")
            return False
        
        return True
    except ValueError as e:
        logger.error(f"Error validating URL {url}: {e}")
        return False

def format_error_message(field: Any, error: Union[str, Exception]) -> str:
    """
    Format error messages consistently for both HTMX and regular requests.
    """
    error_map = {
        'invalid_format': FlashMessages.INVALID_FORMAT,
        'invalid_date': FlashMessages.INVALID_DATE,
        'invalid_time': FlashMessages.INVALID_TIME,
        'invalid_timezone': FlashMessages.INVALID_TIMEZONE,
        'daylight_saving': FlashMessages.DAYLIGHT_SAVING,
        'future_date': FlashMessages.FUTURE_DATE_REQUIRED,
        'past_date': FlashMessages.PAST_DATE_REQUIRED,
        'timezone_conversion': FlashMessages.TIMEZONE_CONVERSION_ERROR,
        'missing_time': FlashMessages.TIME_REQUIRED,
        'required': FlashMessages.FIELD_REQUIRED
    }
    
    # Return mapped error if available
    for key, msg in error_map.items():
        if key in str(error):
            return msg
            
    # Default formatting
    field_label = getattr(field, 'label', None)
    if field_label:
        return f"{field_label.text}: {error}"
    return f"{field.name if hasattr(field, 'name') else str(field)}: {error}"

def log_audit(user_id, action, object_type=None, object_id=None, before=None, after=None):
    """Create an audit log entry with enhanced error handling and logging"""
    logger = logging.getLogger(__name__)
    try:
        # Ensure audit_log table exists
        from app.extensions import db
        if not db.engine.has_table('audit_log'):
            logger.error("audit_log table does not exist")
            raise RuntimeError("audit_log table not found")
            
        # Validate required fields
        if not user_id:
            logger.error("Missing user_id in audit log")
            raise ValueError("user_id is required")
        if not action:
            logger.error("Missing action in audit log")
            raise ValueError("action is required")
        
        # Validate object_type and object_id consistency
        if object_type and not object_id:
            raise ValueError("object_id is required when object_type is provided")
        if object_id and not object_type:
            raise ValueError("object_type is required when object_id is provided")
            
        # Validate action length
        if len(action) > 100:
            raise ValueError("Action exceeds maximum length of 100 characters")
            
        # Validate object_type length
        if object_type and len(object_type) > 50:
            raise ValueError("Object type exceeds maximum length of 50 characters")
        
        # Create audit log
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            object_type=object_type,
            object_id=object_id,
            details_before=json.dumps(before) if before else None,
            details_after=json.dumps(after) if after else None,
            ip_address=request.remote_addr if request else None,
            http_method=request.method if request else None,
            endpoint=request.endpoint if request else None
        )
        
        # Add and commit within a transaction
        with db_session_scope() as session:
            session.add(audit_log)
            session.commit()
            
        logger.info(f"Audit log created: {action} by user {user_id}")
        return audit_log
        
    except Exception as e:
        logger.error(f"Failed to create audit log: {str(e)}", exc_info=True)
        db.session.rollback()
        raise
    """Create an audit log entry with enhanced error handling"""
    try:
        # Validate required fields
        if not user_id:
            raise ValueError("user_id is required")
        if not action:
            raise ValueError("action is required")
        
        # Create audit log
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            object_type=object_type,
            object_id=object_id,
            details_before=json.dumps(before) if before else None,
            details_after=json.dumps(after) if after else None,
            ip_address=request.remote_addr if request else None,
            http_method=request.method if request else None,
            endpoint=request.endpoint if request else None
        )
        
        # Add and commit within a transaction
        with db_session_scope() as session:
            session.add(audit_log)
            session.commit()
            
        logger.info(f"Audit log created: {action} by user {user_id}")
        return audit_log
        
    except Exception as e:
        logger.error(f"Failed to create audit log: {str(e)}", exc_info=True)
        db.session.rollback()
        raise

def create_notification(type, message, related_object=None, user_id=None):
    """Create a notification"""
    try:
        notification = Notification(
            type=type,
            message=message,
            related_object=related_object,
            user_id=user_id
        )
        db.session.add(notification)
        db.session.commit()
    except Exception as e:
        logger.error(f"Failed to create notification: {e}")
        db.session.rollback()

def flash_message(message, category):
    from flask import flash
    try:
        flash(message, category)
        # Log important messages
        if category == FlashCategory.ERROR:
            logger.error(f"Flash Error: {message}")
        elif category == FlashCategory.WARNING:
            logger.warning(f"Flash Warning: {message}")
    except Exception as e:
        logger.error(f"Failed to flash message: {e}")
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from bleach import clean as bleach_clean

def clean(text, tags=None, attributes=None):
    """Sanitize input text using bleach."""
    if not text:
        return text
    return bleach_clean(text, tags=tags, attributes=attributes)

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

def setup_rate_limits(app):
    limiter.init_app(app)
    
    # Import services locally to avoid circular imports
    from app.services.stipend_service import StipendService
    stipend_service = StipendService()
    
    # CRUD specific limits
    limiter.limit("10/minute")(stipend_service.create_stipend)
    limiter.limit("10/minute")(stipend_service.update_stipend)
    limiter.limit("3/minute")(stipend_service.delete_stipend)
    
    # Bot operations rate limits would be set in bot_service
from contextlib import contextmanager
from datetime import datetime, timedelta
from croniter import croniter

def calculate_next_run(schedule):
    """Calculate the next run time based on a cron-like schedule."""
    if not schedule:
        return None
    try:
        now = datetime.now()
        cron = croniter(schedule, now)
        return cron.get_next(datetime)
    except ImportError as e:
        logger.error("croniter package not installed. Run 'pip install croniter'")
        raise RuntimeError("Required package 'croniter' not installed. Please install it first.")
    except Exception as e:
        logger.error(f"Error calculating next run time: {str(e)}")
        raise ValueError(f"Invalid schedule format: {str(e)}. Expected cron format like '0 0 * * *'")

@contextmanager
def db_session_scope():
    """Provide a transactional scope around a series of operations."""
    session = db.session
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database operation failed: {str(e)}")
        raise
    finally:
        # Ensure session is properly closed
        session.close()

def htmx_response(template, context=None, status=200, headers=None):
    """Helper for creating HTMX responses"""
    if context is None:
        context = {}
    if headers is None:
        headers = {}
        
    headers['HX-Trigger'] = 'pageUpdate'
    return render_template(template, **context), status, headers

def log_operation(operation):
    """Decorator for logging operations"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                current_app.logger.info(f"{operation} completed successfully")
                return result
            except Exception as e:
                current_app.logger.error(f"{operation} failed: {str(e)}")
                raise
        return wrapper
from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def login_required(role="user"):
    """Decorator to require login with optional role checking"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            if role != "user" and current_user.role != role:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('main.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
