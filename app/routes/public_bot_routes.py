from flask import Blueprint

public_bot_bp = Blueprint('public_bot', __name__)

# Define your routes here
@public_bot_bp.route('/public/bot')
def public_bot():
    return "Public Bot Route"
