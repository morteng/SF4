from flask import Blueprint, request, jsonify
from app.utils import login_required
from app.services.bot_service import create_bot

bot_bp = Blueprint('admin', __name__, url_prefix='/admin')

@bot_bp.route('/bots', methods=['POST'])
@login_required
def create_bot():
    data = request.get_json()
    bot = create_bot(data['name'], data['description'], data['status'])
    return jsonify(bot), 201
