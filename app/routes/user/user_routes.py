from flask import Blueprint

# Create the user blueprint
user_bp = Blueprint('user', __name__)

# Example route for demonstration purposes
@user_bp.route('/profile')
def profile():
    return "User Profile Page"
