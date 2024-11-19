from flask import Blueprint

bot_bp = Blueprint('bot', __name__, url_prefix='/bots')

# Example route for demonstration purposes
@bot_bp.route('/create', methods=['POST'])
def create_bot():
    # Your logic here
    return "Bot created"
