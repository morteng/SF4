from flask import Blueprint

# Create a blueprint for the user routes
user_bp = Blueprint('user', __name__)

@user_bp.route('/profile')
def profile():
    return "User Profile"

@user_bp.route('/settings')
def settings():
    return "User Settings"
