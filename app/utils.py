from flask import request, jsonify
from functools import wraps
from app.models.user import User

def admin_required(f):
    """
    Decorator to check if the user is an admin.
    
    Expects a valid auth token in the Authorization header.
    
    Args:
        f (function): The function to be decorated.
        
    Returns:
        function: The decorated function.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get the token from the request headers
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({'message': 'Missing or invalid token'}), 401
        
        # Extract the actual token part
        token = token.split()[1]
        
        # Verify the token and get the user
        admin_user = User.verify_auth_token(token)
        if not admin_user or not admin_user.is_admin:
            return jsonify({'message': 'Unauthorized access'}), 403
        
        # Call the original function with the admin user as an argument
        return f(admin_user, *args, **kwargs)
    
    return decorated_function
