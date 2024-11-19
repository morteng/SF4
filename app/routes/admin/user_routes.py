from flask import Blueprint

user_bp = Blueprint('admin_user', __name__)

# Define your routes here, for example:
@user_bp.route('/users')
def list_users():
    return "List of users"

@user_bp.route('/greet')
def greet():
    return "Hey there!"
