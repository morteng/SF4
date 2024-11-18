from flask import Blueprint

bp = Blueprint('public_bot', __name__)

# Define your routes here
@bp.route('/some-bot-route')
def some_bot_route():
    return "Bot Route!"
