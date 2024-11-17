from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import User
from app.extensions import db
from app.utils import admin_required

admin_user_bp = Blueprint('admin_user', __name__, url_prefix='/admin/users')

@admin_user_bp.route('/login', methods=['POST'])
def admin_login():
    """
    Logs in an admin user.
    
    Expects a JSON payload with 'username' and 'password'.
    
    Returns:
        jsonify: A message indicating success or failure.
    """
    data = request.get_json()
    username = data['username']
    password = data['password']

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password_hash, password) or not user.is_admin:
        return jsonify({'message': 'Invalid credentials'}), 401

    token = user.generate_auth_token()
    return jsonify({
        'message': 'Admin login successful',
        'user_id': user.id,
        'token': token
    }), 200

@admin_user_bp.route('/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """
    Updates an existing user.
    
    Expects a JSON payload with updated user details.
    
    Args:
        user_id (int): The ID of the user to be updated.
        
    Returns:
        jsonify: A message indicating success and the updated user's ID.
    """
    data = request.get_json()
    user = User.query.get_or_404(user_id)

    user.username = data['username']
    user.set_password(data['password'])
    user.email = data['email']
    user.is_admin = data['is_admin']

    db.session.commit()

    return jsonify({
        'message': 'User updated successfully',
        'user_id': user.id
    }), 200

@admin_user_bp.route('/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """
    Deletes a user.
    
    Args:
        user_id (int): The ID of the user to be deleted.
        
    Returns:
        jsonify: A message indicating success and the deleted user's ID.
    """
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    return jsonify({
        'message': 'User deleted successfully',
        'user_id': user.id
    }), 200
