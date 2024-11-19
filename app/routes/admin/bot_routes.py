from flask import Blueprint, request, jsonify
from app.utils import login_required
from app.services.bot_service import create_bot

bot_admin_bp = Blueprint('bot_admin', __name__, url_prefix='/bots')  # Renamed to 'bot_admin'

@bot_admin_bp.route('', methods=['POST'])
@login_required
def create_bot():
    data = request.get_json()
    bot = create_bot(data['name'], data['description'], data['status'])
    return jsonify(bot), 201
