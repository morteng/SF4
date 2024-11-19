from flask import Blueprint, request, jsonify
from app.services.bot_service import create_bot

bot_bp = Blueprint('admin_bot', __name__)

@bot_bp.route('/bots/create', methods=['POST'])
def create_bot_route():
    data = request.form
    name = data.get('name')
    description = data.get('description')
    status = data.get('status')

    if not name or not description or not status:
        return jsonify({"message": "Name, description, and status are required"}), 400

    bot = create_bot(name, description, status)
    if bot:
        return jsonify({"message": "Bot created successfully", "bot_id": bot.id}), 200
    else:
        return jsonify({"message": "Failed to create bot"}), 500
