from flask import Blueprint, request, jsonify, abort
from app.models.bot import Bot
from app.extensions import db
from datetime import datetime
import logging

bot_bp = Blueprint('bot', __name__)

@bot_bp.route('/bots/<int:bot_id>/run', methods=['POST'])
def run_bot(bot_id):
    bot = Bot.query.get_or_404(bot_id)

    # Simulate running the bot
    bot.last_run = datetime.utcnow()
    db.session.commit()

    logging.info(f"Bot {bot.name} has been run successfully")
    return jsonify({
        'message': f'Bot {bot.name} has been run successfully',
        'last_run': bot.last_run
    }), 200

@bot_bp.route('/bots/<int:bot_id>/status', methods=['GET'])
def get_bot_status(bot_id):
    bot = Bot.query.get_or_404(bot_id)

    return jsonify({
        'name': bot.name,
        'description': bot.description,
        'status': bot.status,
        'last_run': bot.last_run
    }), 200

@bot_bp.route('/bots/<int:bot_id>/logs', methods=['GET'])
def get_bot_logs(bot_id):
    bot = Bot.query.get_or_404(bot_id)

    return jsonify({
        'name': bot.name,
        'error_log': bot.error_log
    }), 200

@bot_bp.route('/bot/status')
def bot_status():
    return jsonify({"message": "Bot is running"}), 200

@bot_bp.errorhandler(404)
def bot_not_found(error):
    logging.warning(f"Bot not found: {request.url}")
    return jsonify({"error": "Bot not found"}), 404
