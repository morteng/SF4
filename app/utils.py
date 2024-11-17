from functools import wraps
from flask import jsonify, request
from app.models.user import User
from app.extensions import db  # Import the db object

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

def init_admin_user():
    """Initialize admin user if it doesn't exist"""
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@example.com',
            is_admin=True
        )
        admin.set_password('admin')  # Set a default password
        db.session.add(admin)
        db.session.commit()
        admin.generate_auth_token()  # Generate initial token
    return admin
