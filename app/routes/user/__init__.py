from flask import Blueprint, request, jsonify, session
from app.utils import login_required
from app.services.user_service import create_user, get_user_by_username, authenticate_user

user_bp = Blueprint('user', __name__, url_prefix='/users')

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    
    user = get_user_by_username(username)
    if user and user.check_password(password):
        session['user_id'] = user.id
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401

@user_bp.route('/create', methods=['POST'])
def create_user_route():
    data = request.get_json()
    user = create_user(data['username'], data['password'], data['email'])
    return jsonify(user), 201
