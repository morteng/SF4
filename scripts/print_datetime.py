from datetime import datetime
from flask import abort, redirect, url_for
from flask_login import current_user, login_required as _login_required  # Import the original login_required

def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return abort(403)
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Define login_required in utils.py
login_required = _login_required

def format_datetime(dt=None, fmt='%Y-%m-%d %H:%M:%S'):
    """Format a datetime object or the current time.
    
    Args:
        dt (datetime, optional): The datetime object to format. Defaults to None (current time).
        fmt (str, optional): The format string. Defaults to '%Y-%m-%d %H:%M:%S'.
    
    Returns:
        str: The formatted datetime string.
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime(fmt)

# Print the current datetime to console
if __name__ == "__main__":
    print(format_datetime())
