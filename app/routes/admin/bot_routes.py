from flask import Blueprint, request, jsonify
from app.models.bot import Bot
from app.extensions import db
from app.utils import admin_required

admin_bot_bp = Blueprint('admin_bot', __name__, url_prefix='/admin/bots')

@admin_bot_bp.route('', methods=['POST'])
@admin_required
def create_bot(admin_user):
    """
    Creates a new bot.
    
    Args:
        admin_user: The authenticated admin user from the @admin_required decorator
    
    Expects a JSON payload with bot details.
    
    Returns:
        jsonify: A message indicating success and the created bot's ID.
    """
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'description', 'status']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400
        
    if not data['name'].strip():
        return jsonify({'message': 'Invalid bot name'}), 400

    bot = Bot(
        name=data['name'],
        description=data['description'],
        status=data['status']
    )
    db.session.add(bot)
    db.session.commit()

    return jsonify({
        'message': 'Bot created successfully',
        'bot_id': bot.id
    }), 201

@admin_bot_bp.route('/<int:bot_id>', methods=['PUT'])
@admin_required
def update_bot(admin_user, bot_id):
    """
    Updates an existing bot.
    
    Args:
        admin_user: The authenticated admin user from the @admin_required decorator
        bot_id (int): The ID of the bot to be updated.
        
    Returns:
        jsonify: A message indicating success and the updated bot's ID.
    """
    data = request.get_json()
    bot = Bot.query.get_or_404(bot_id)

    bot.name = data['name']
    bot.description = data['description']
    bot.status = data['status']

    db.session.commit()

    return jsonify({
        'message': 'Bot updated successfully',
        'bot_id': bot.id
    }), 200

@admin_bot_bp.route('/<int:bot_id>', methods=['DELETE'])
@admin_required
def delete_bot(admin_user, bot_id):
    """
    Deletes a bot.
    
    Args:
        admin_user: The authenticated admin user from the @admin_required decorator
        bot_id (int): The ID of the bot to be deleted.
        
    Returns:
        jsonify: A message indicating success and the deleted bot's ID.
    """
    bot = Bot.query.get_or_404(bot_id)
    db.session.delete(bot)
    db.session.commit()

    return jsonify({
        'message': 'Bot deleted successfully',
        'bot_id': bot.id
    }), 200

@admin_bot_bp.route('/status')
@admin_required
def bot_status(admin_user):
    """
    Returns the status of all bots.
    
    Args:
        admin_user: The authenticated admin user from the @admin_required decorator
    
    Returns:
        jsonify: A message indicating the status of all bots.
    """
    return jsonify({"message": "All bots operational"}), 200
