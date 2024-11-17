from flask import Blueprint, jsonify

bot_bp = Blueprint('bot', __name__, url_prefix='/bot')

@bot_bp.route('/status')
def bot_status():
    return jsonify({"status": "All bots operational"}), 200
