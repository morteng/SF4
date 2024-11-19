from flask import Blueprint, request, jsonify, session
from app.models.user import User

user_bp = Blueprint('admin', __name__, url_prefix='/admin')

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.form
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        session['user_id'] = user.id
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401
