# app/routes/public_bot_routes.py

from flask import Blueprint, jsonify
from app.models.bot import Bot

public_bot_bp = Blueprint('public_bot', __name__)

@public_bot_bp.route('/bots/status')
def bots_status():
    bots = Bot.query.all()
    bots_info = [{'name': bot.name, 'status': bot.status, 'last_run': bot.last_run} for bot in bots]
    return jsonify(bots_info)
