from flask import Blueprint, jsonify

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/index')
def user_index():
    return jsonify({"message": "User index page"}), 200

@user_bp.route('/profile/<int:user_id>')
def user_profile(user_id):
    return jsonify({"message": f"Profile for user {user_id}"}), 200
