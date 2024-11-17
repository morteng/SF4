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
    from os import environ
    
    admin_username = environ.get('ADMIN_USERNAME', 'admin_user')
    admin_email = environ.get('ADMIN_EMAIL', 'admin@example.com')
    admin_password = environ.get('ADMIN_PASSWORD', 'admin')

    admin = User.query.filter(
        (User.username == admin_username) | 
        (User.email == admin_email)
    ).first()
    
    if not admin:
        try:
            admin = User(
                username=admin_username,
                email=admin_email,
                is_admin=True
            )
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()
            print(f"Created admin user: {admin_username}")
            admin.generate_auth_token()  # Generate initial token
        except Exception as e:
            print(f"Error creating admin user: {e}")
            db.session.rollback()
    
    return admin
