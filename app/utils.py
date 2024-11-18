from flask import request, jsonify, current_app
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
        
        current_app.logger.debug(f"Received Authorization header: {token}")
        
        if not token or not token.startswith('Bearer '):
            current_app.logger.debug("Missing or invalid token format")
            return jsonify({'message': 'Missing or invalid token'}), 401
        
        # Extract the actual token part
        token = token.split()[1]
        current_app.logger.debug(f"Extracted token: {token}")
        
        # Verify the token and get the user
        admin_user = User.verify_auth_token(token)
        if not admin_user:
            current_app.logger.debug("Token verification failed")
            return jsonify({'message': 'Invalid token'}), 401
            
        if not admin_user.is_admin:
            current_app.logger.debug(f"User {admin_user.username} is not an admin")
            return jsonify({'message': 'Unauthorized access'}), 403
        
        current_app.logger.debug(f"Admin authentication successful for user {admin_user.username}")
        return f(admin_user, *args, **kwargs)
    
    return decorated_function
