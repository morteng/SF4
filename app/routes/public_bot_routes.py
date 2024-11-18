from flask import Blueprint

public_bot_bp = Blueprint('public_bot', __name__)

# Define your routes here
@public_bot_bp.route('/some-bot-route')
def some_bot_route():
    return "Bot Route!"
