from flask import Blueprint, jsonify

public_user_bp = Blueprint('public_user', __name__, url_prefix='/user')

@public_user_bp.route('/index')
def user_index():
    return jsonify({"message": "Public user index page"}), 200

@public_user_bp.route('/profile/<int:user_id>')
def user_profile(user_id):
    return jsonify({"message": f"Public profile for user {user_id}"}), 200
