from flask_login import current_user
from flask import redirect, url_for, flash
from functools import wraps
from flask_login import login_required
# AI: add docstrings to all functions, methods, and classes
def admin_required(func):
    @login_required
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_admin:
            flash('You do not have permission to view this page.', 'danger')
            return redirect(url_for('visitor.index'))
        return func(*args, **kwargs)
    return decorated_view
