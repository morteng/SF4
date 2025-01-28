import os
import logging
import string
import secrets
import json
import re

from datetime import datetime, timezone
from typing import Any, Union, Tuple
from functools import wraps
from urllib.parse import urlparse

from flask import abort, redirect, url_for, flash, request, current_app, render_template
from flask_login import current_user, login_required as flask_login_required
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import generate_csrf
from bleach import clean as bleach_clean
from itsdangerous import URLSafeTimedSerializer
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
from croniter import croniter

from app.models.audit_log import AuditLog
from app.models.notification import Notification
from app.models.user import User
from app.extensions import db
from app.constants import FlashMessages, FlashCategory
from contextlib import contextmanager

logger = logging.getLogger(__name__)

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

def generate_csrf_token():
    """Generate a CSRF token for form validation."""
    return generate_csrf()

def decode_csrf_token(encoded_token):
    """Decode a CSRF token from its encoded form."""
    serializer = URLSafeTimedSerializer(
        current_app.config['SECRET_KEY'],
        salt='csrf-token'
    )
    try:
        # No expiration set here; consider max_age if you want time-limited tokens
        return serializer.loads(encoded_token, max_age=None)
    except Exception as e:
        logger.error(f"Failed to decode CSRF token: {str(e)}")
        raise

def validate_password_strength(password: str) -> bool:
    """Validate password strength according to project requirements."""
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

    # Check against common passwords
    common_passwords = ['password', '123456', 'qwerty']
    if password.lower() in common_passwords:
        return False

    return True

def get_unread_notification_count() -> int:
    """Get count of unread notifications."""
    return Notification.query.filter_by(read_status=False).count()

def generate_temp_password(length: int = 12) -> str:
    """Generate a temporary password."""
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(chars) for _ in range(length))

def validate_url(url: str) -> bool:
    """
    Validate URL format according to RFC standards:
    - Must start with http:// or https://
    - Must be properly formatted
    """
    if not url:
        logger.warning("Empty URL provided for validation.")
        return False

    try:
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

    for key, msg in error_map.items():
        if key in str(error):
            return msg

    field_label = getattr(field, 'label', None)
    if field_label:
        return f"{field_label.text}: {error}"
    return f"{field.name if hasattr(field, 'name') else str(field)}: {error}"

def setup_rate_limits(app):
    """Set up rate limits on certain endpoints or services."""
    limiter.init_app(app)
    from app.services.stipend_service import StipendService
    stipend_service = StipendService()

    limiter.limit("10/minute")(stipend_service.create_stipend)
    limiter.limit("10/minute")(stipend_service.update_stipend)
    limiter.limit("3/minute")(stipend_service.delete_stipend)

def calculate_next_run(schedule):
    """Calculate the next run time based on a cron-like schedule."""
    if not schedule:
        return None
    try:
        now = datetime.now()
        c = croniter(schedule, now)
        return c.get_next(datetime)
    except Exception as e:
        logger.error(f"Error calculating next run time: {str(e)}")
        raise ValueError(f"Invalid schedule format: {str(e)}. Expected cron format like '0 0 * * *'")

@contextmanager
def db_session_scope():
    """Provide a transactional scope for DB operations."""
    session = db.session
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database operation failed: {str(e)}")
        raise
    finally:
        session.close()

def htmx_response(template, context=None, status=200, headers=None):
    """Helper for creating HTMX responses."""
    if context is None:
        context = {}
    if headers is None:
        headers = {}

    headers['HX-Trigger'] = 'pageUpdate'
    return render_template(template, **context), status, headers

def log_operation(operation):
    """Decorator for logging function calls."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                current_app.logger.info(f"{operation} completed successfully")
                return result
            except Exception as e:
                current_app.logger.error(f"{operation} failed: {str(e)}")
                raise
        return wrapper
    return decorator

def role_required(role="user"):
    """
    Decorator to require login with optional role checking,
    renamed to avoid confusion with Flask-Login's built-in login_required.
    """
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
