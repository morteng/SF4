# app/utils.py
import os
from flask import abort, redirect, url_for, flash
from flask_login import current_user, login_required as _login_required  # Import the original login_required
from .models.user import User
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv  # Add this import
from app.extensions import db  # Import the db object

def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return abort(403)
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Define login_required in utils.py
login_required = _login_required

def init_admin_user():
    load_dotenv()  # Load environment variables from .env file
    username = os.environ.get('ADMIN_USERNAME')
    password = os.environ.get('ADMIN_PASSWORD')
    email = os.environ.get('ADMIN_EMAIL')

    if not User.query.filter_by(username=username).first():
        admin_user = User(
            username=username,
            password_hash=generate_password_hash(password),
            email=email,
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()

def format_error_message(field, error):
    """Format error messages consistently for both HTMX and regular requests"""
    import logging
    logging.debug(f"Formatting error for field '{getattr(field, 'name', str(field))}': {error}")
    field_name = getattr(field, 'name', str(field))
    
    # Handle date-specific errors
    if field_name == 'application_deadline':
        error_str = str(error)
        # Format validation errors
        if 'does not match format' in error_str or 'invalid-date' in error_str:
            return 'Invalid date format. Please use YYYY-MM-DD HH:MM:SS'
        # Date component errors
        elif 'Invalid month value' in error_str or 'month is out of range' in error_str:
            return 'Invalid month value (1-12)'
        elif 'Invalid day value' in error_str or 'day is out of range' in error_str:
            return 'Invalid day for month'
        elif 'Invalid year value' in error_str:
            return 'Invalid year value'
        # Time component errors
        elif 'Invalid hour value' in error_str:
            return 'Invalid hour value (0-23)'
        elif 'Invalid minute value' in error_str:
            return 'Invalid minute value (0-59)'
        elif 'Invalid second value' in error_str:
            return 'Invalid second value (0-59)'
        # Date range errors
        elif 'must be a future date' in error_str:
            return 'Application deadline must be a future date'
        elif 'cannot be more than 5 years' in error_str:
            return 'Application deadline cannot be more than 5 years in the future'
        # Required field errors
        elif 'Time is required' in error_str:
            return 'Time is required. Please use YYYY-MM-DD HH:MM:SS'
        elif 'Date is required' in error_str:
            return 'Date is required'
        # General date/time errors
        elif 'Invalid date/time values' in error_str:
            return 'Invalid date/time values'
        # Remove field label prefix for HTMX responses
        return str(error).replace('Application Deadline: ', '')
    
    # Handle other field errors consistently
    field_label = getattr(field, 'label', None)
    if field_label:
        return f"{field_label.text}: {error}"
    return f"{field_name}: {error}"

def flash_message(message, category):
    from flask import flash
    flash(message, category)
