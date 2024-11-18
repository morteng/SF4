from flask import Blueprint

public_user_bp = Blueprint('public_user', __name__)

# Define your routes here
@public_user_bp.route('/some-route')
def some_route():
    return "Hey there!"
