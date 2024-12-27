# app/utils.py
import os
import logging
import string
import secrets
from typing import Any, Union
from flask import abort, redirect, url_for, flash
from flask_wtf.csrf import generate_csrf
from app.models.audit_log import AuditLog

def generate_csrf_token():
    """Generate a CSRF token for form validation."""
    return generate_csrf()

# Configure logging
logger = logging.getLogger(__name__)
from flask_login import current_user, login_required as _login_required  # Import the original login_required
from .models.user import User
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv  # Add this import
from app.extensions import db  # Import the db object

def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash_message(FlashMessages.LOGIN_REQUIRED.value, FlashCategory.ERROR.value)
            return redirect(url_for('public.login'))
            
        if not current_user.is_admin:
            flash_message(FlashMessages.ADMIN_REQUIRED.value, FlashCategory.ERROR.value)
            return abort(403)
            
        # Add audit log
        audit_log = AuditLog(
            user_id=current_user.id,
            action=f.__name__,
            details=f"Accessed admin route: {request.path}",
            timestamp=datetime.utcnow()
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Define login_required in utils.py
login_required = _login_required

def init_admin_user() -> None:
    """
    Initialize the admin user from environment variables.
    
    Raises:
        RuntimeError: If required environment variables are missing
    """
    try:
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
    """Validate password strength.
    
    Args:
        password: Password to validate
        
    Returns:
        bool: True if password meets strength requirements
    """
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    if not re.search(r'[^A-Za-z0-9]', password):
        return False
    return True

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
    """Validate URL format.
    
    Args:
        url: URL string to validate
        
    Returns:
        bool: True if URL is valid, False otherwise
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
    
    Args:
        field: The form field that generated the error
        error: The error message or exception
        
    Returns:
        str: Formatted error message with field name/label
    """
    error_map = {
        'invalid_format': 'Invalid format. Please use YYYY-MM-DD HH:MM:SS',
        'invalid_date': 'Invalid date values',
        'invalid_time': 'Invalid time values',
        'invalid_timezone': 'Invalid timezone selected',
        'daylight_saving': 'Ambiguous time due to daylight saving',
        'future_date': 'Date must be in the future',
        'past_date': 'Date must be in the past',
        'timezone_conversion': 'Error converting timezone',
        'missing_time': 'Time is required',
        'required': 'This field is required'
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

def flash_message(message, category):
    from flask import flash
    flash(message, category)
