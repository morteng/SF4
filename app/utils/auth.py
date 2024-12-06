from flask_login import current_user
from flask import redirect, url_for, flash
from functools import wraps
from flask_login import login_required

def admin_required(func):
    """
    Decorator to restrict access to views to admin users only.

    Args:
        func (function): The view function to decorate.

    Returns:
        function: The decorated function.
    """
    @login_required
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_admin:
            flash('You do not have permission to view this page.', 'danger')
            return redirect(url_for('visitor.index'))
        return func(*args, **kwargs)
    return decorated_view
