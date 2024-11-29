from flask import request, jsonify
from app.extensions import db
from app.models.bot import Bot
from app.services.bot_service import create_bot
from app.routes.api import api_bp
from app.utils import login_required

@api_bp.route('/bots', methods=['POST'])
@login_required
def api_create_bot():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    status = data.get('status')

    if not all([name, description, status]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        bot = create_bot(name, description, status)
        db.session.add(bot)
        db.session.commit()
        return jsonify(bot.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
