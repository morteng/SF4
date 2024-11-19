from flask import session, abort
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            abort(401)
        from app.models.user import User
        user = User.query.get(user_id)
        if not user or not user.is_admin:
            abort(403)  # Forbidden if not an admin
        return f(*args, **kwargs)
    return decorated_function
