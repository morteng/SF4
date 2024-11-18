from flask import Blueprint, jsonify, request
from app.models.user import User
from app.models.bot import Bot
from app.models.stipend import Stipend
from app.models.tag import Tag
from app.models.organization import Organization
from app.models.notification import Notification
from werkzeug.security import generate_password_hash

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/login', methods=['POST'])
def admin_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password) and user.is_admin:
        return jsonify({"message": "Admin login successful"}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401

@admin_bp.route('/bots', methods=['POST'])
def create_bot():
    data = request.json
    name = data.get('name')
    description = data.get('description')
    status = data.get('status')
    
    if not name or not description or not status:
        return jsonify({"message": "Missing fields"}), 400
    
    bot = Bot(name=name, description=description, status=status)
    db.session.add(bot)
    db.session.commit()
    return jsonify({"bot_id": bot.bot_id}), 201

@admin_bp.route('/bots/<int:bot_id>', methods=['PUT'])
def update_bot(bot_id):
    data = request.json
    name = data.get('name')
    description = data.get('description')
    status = data.get('status')
    
    bot = Bot.query.get(bot_id)
    if not bot:
        return jsonify({"message": "Bot not found"}), 404
    
    if name:
        bot.name = name
    if description:
        bot.description = description
    if status:
        bot.status = status
    
    db.session.commit()
    return jsonify({"message": "Bot updated successfully"}), 200

@admin_bp.route('/bots/<int:bot_id>', methods=['DELETE'])
def delete_bot(bot_id):
    bot = Bot.query.get(bot_id)
    if not bot:
        return jsonify({"message": "Bot not found"}), 404
    
    db.session.delete(bot)
    db.session.commit()
    return jsonify({"message": "Bot deleted successfully"}), 200

# Add similar routes for stipends, tags, organizations, and notifications
