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
    field_name = getattr(field, 'name', str(field))
    
    # Handle date-specific errors
    if field_name == 'application_deadline':
        if 'invalid_format' in error:
            return 'Invalid date format. Please use YYYY-MM-DD HH:MM:SS'
        elif 'invalid_date' in error:
            return 'Invalid date values (e.g., Feb 30)'
        elif 'invalid_time' in error:
            return 'Invalid time values (e.g., 25:61:61)'
        elif 'missing_time' in error:
            return 'Time is required. Please use YYYY-MM-DD HH:MM:SS'
        elif 'required' in error:
            return 'Date is required'
        elif 'cannot be in the past' in error:
            return 'Application deadline must be a future date'
        elif 'cannot be more than 5 years' in error:
            return 'Application deadline cannot be more than 5 years in the future'
        return error
    
    # Get the field label if available
    field_label = getattr(field, 'label', None)
    if field_label:
        return f"{field_label.text}: {error}"
    return f"{field_name}: {error}"

def flash_message(message, category):
    from flask import flash
    flash(message, category)
