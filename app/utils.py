from functools import wraps
from flask import jsonify, request
from app.models.user import User

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'message': 'No authorization header'}), 401
            
        try:
            # Assuming Bearer token format
            token = auth_header.split(' ')[1]
            user = User.verify_auth_token(token)
            if not user or not user.is_admin:
                return jsonify({'message': 'Unauthorized access'}), 403
        except Exception as e:
            return jsonify({'message': 'Invalid token', 'error': str(e)}), 401
            
        return f(*args, **kwargs)
    return decorated_function
