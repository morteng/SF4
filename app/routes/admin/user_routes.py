from flask import Blueprint, request, jsonify, session
import logging
from app.models.user import User

admin_user_bp = Blueprint('admin_user', __name__, url_prefix='/users')  # Renamed to 'admin_user'

@admin_user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()  # Changed from request.form to request.get_json
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        session['user_id'] = user.id
        logging.info(f"User {username} logged in successfully. Session ID: {session.sid}")
        return jsonify({"message": "Login successful"}), 200
    else:
        logging.info(f"Failed login attempt for username: {username}")
        return jsonify({"message": "Invalid credentials"}), 401
