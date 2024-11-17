from flask import Blueprint, jsonify

public_bot_bp = Blueprint('public_bot', __name__, url_prefix='/bot')

@public_bot_bp.route('/status')
def bot_status():
    return jsonify({"message": "Public bot status"}), 200
