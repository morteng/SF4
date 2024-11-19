from flask import Blueprint, request, jsonify
from app.utils import login_required
from app.services.bot_service import create_bot

# Use a unique name for the blueprint
bot_admin_bp = Blueprint('admin_bot_admin', __name__, url_prefix='/bots')

@bot_admin_bp.route('', methods=['POST'])
@login_required
def create_bot_route():
    data = request.get_json()
    bot = create_bot(data['name'], data['description'], data['status'])
    return jsonify(bot), 201
