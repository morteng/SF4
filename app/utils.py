# app/utils.py
from flask import abort, redirect, url_for
from flask_login import current_user, login_required as _login_required  # Import the original login_required
# AI: add docstrings to all functions, methods, and classes AI!
def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return abort(403)
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Define login_required in utils.py
login_required = _login_required

def greeting(name):
    print(f"Hey {name}")
