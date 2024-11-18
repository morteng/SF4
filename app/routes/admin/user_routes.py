from flask import Blueprint, request, jsonify, session
from app.models.user import User
from werkzeug.security import check_password_hash

admin_user_bp = Blueprint('admin_user', __name__)

@admin_user_bp.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password) and user.is_admin:
        session['user_id'] = user.id
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401
