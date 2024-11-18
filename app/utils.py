from flask import request, jsonify
from functools import wraps
from app.models.user import User

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Extract the token from the Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'message': 'Missing or invalid Bearer token'}), 401

        token = auth_header.split()[1]
        user = User.verify_auth_token(token)

        # Check if the user is an admin
        if not user or not user.is_admin:
            return jsonify({'message': 'Forbidden: Admin access required'}), 403

        return f(*args, **kwargs)
    return decorated_function
