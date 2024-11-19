from flask import Blueprint

public_bot_bp = Blueprint('public_bot', __name__)

# Define your routes here
@public_bot_bp.route('/public/bots', methods=['GET'])
def public_bot():
    return render_template('public/bot_list.html')
