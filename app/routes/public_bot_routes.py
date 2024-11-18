from flask import Blueprint

public_bot_bp = Blueprint('public_bot', __name__)

# Define your routes here
@public_bot_bp.route('/public/bot')
def public_bot():
    return "Public Bot Route"
from flask import Blueprint

user_bp = Blueprint('public_user', __name__)

# Define your routes here
@user_bp.route('/public/user')
def public_user():
    return "Public User Route"
