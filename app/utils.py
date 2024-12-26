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
