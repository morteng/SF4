from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import User
from app.models.stipend import Stipend
from app.models.tag import Tag
from app.models.organization import Organization
from app.models.bot import Bot
from app.models.notification import Notification
from app.extensions import db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/login', methods=['POST'])
def admin_login():
    """
    Logs in an admin user.
    
    Expects a JSON payload with 'username' and 'password'.
    
    Returns:
        jsonify: A message indicating success or failure.
    """
    data = request.get_json()
    username = data['username']
    password = data['password']

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password_hash, password) or not user.is_admin:
        return jsonify({'message': 'Invalid credentials'}), 401

    return jsonify({
        'message': 'Admin login successful',
        'user_id': user.id
    }), 200

@admin_bp.route('/admin')
def admin_index():
    """
    Returns a greeting message for the admin.
    
    Returns:
        str: A greeting message.
    """
    return 'Hello Admin!', 200

@admin_bp.route('/admin/stipends', methods=['POST'])
def create_stipend():
    """
    Creates a new stipend.
    
    Expects a JSON payload with stipend details.
    
    Returns:
        jsonify: A message indicating success and the created stipend's ID.
    """
    data = request.get_json()
    stipend = Stipend(
        name=data['name'],
        summary=data['summary'],
        description=data['description'],
        homepage_url=data['homepage_url'],
        application_procedure=data['application_procedure'],
        eligibility_criteria=data['eligibility_criteria'],
        application_deadline=data['application_deadline'],
        open_for_applications=data['open_for_applications']
    )
    db.session.add(stipend)
    db.session.commit()

    return jsonify({
        'message': 'Stipend created successfully',
        'stipend_id': stipend.id
    }), 201

@admin_bp.route('/admin/stipends/<int:stipend_id>', methods=['PUT'])
def update_stipend(stipend_id):
    """
    Updates an existing stipend.
    
    Expects a JSON payload with updated stipend details.
    
    Args:
        stipend_id (int): The ID of the stipend to be updated.
        
    Returns:
        jsonify: A message indicating success and the updated stipend's ID.
    """
    data = request.get_json()
    stipend = Stipend.query.get_or_404(stipend_id)

    stipend.name = data['name']
    stipend.summary = data['summary']
    stipend.description = data['description']
    stipend.homepage_url = data['homepage_url']
    stipend.application_procedure = data['application_procedure']
    stipend.eligibility_criteria = data['eligibility_criteria']
    stipend.application_deadline = data['application_deadline']
    stipend.open_for_applications = data['open_for_applications']

    db.session.commit()

    return jsonify({
        'message': 'Stipend updated successfully',
        'stipend_id': stipend.id
    }), 200

@admin_bp.route('/admin/stipends/<int:stipend_id>', methods=['DELETE'])
def delete_stipend(stipend_id):
    """
    Deletes a stipend.
    
    Args:
        stipend_id (int): The ID of the stipend to be deleted.
        
    Returns:
        jsonify: A message indicating success and the deleted stipend's ID.
    """
    stipend = Stipend.query.get_or_404(stipend_id)
    db.session.delete(stipend)
    db.session.commit()

    return jsonify({
        'message': 'Stipend deleted successfully',
        'stipend_id': stipend.id
    }), 200

@admin_bp.route('/admin/tags', methods=['POST'])
def create_tag():
    """
    Creates a new tag.
    
    Expects a JSON payload with tag details.
    
    Returns:
        jsonify: A message indicating success and the created tag's ID.
    """
    data = request.get_json()
    tag = Tag(
        name=data['name'],
        category=data['category']
    )
    db.session.add(tag)
    db.session.commit()

    return jsonify({
        'message': 'Tag created successfully',
        'tag_id': tag.id
    }), 201

@admin_bp.route('/admin/tags/<int:tag_id>', methods=['PUT'])
def update_tag(tag_id):
    """
    Updates an existing tag.
    
    Expects a JSON payload with updated tag details.
    
    Args:
        tag_id (int): The ID of the tag to be updated.
        
    Returns:
        jsonify: A message indicating success and the updated tag's ID.
    """
    data = request.get_json()
    tag = Tag.query.get_or_404(tag_id)

    tag.name = data['name']
    tag.category = data['category']

    db.session.commit()

    return jsonify({
        'message': 'Tag updated successfully',
        'tag_id': tag.id
    }), 200

@admin_bp.route('/admin/tags/<int:tag_id>', methods=['DELETE'])
def delete_tag(tag_id):
    """
    Deletes a tag.
    
    Args:
        tag_id (int): The ID of the tag to be deleted.
        
    Returns:
        jsonify: A message indicating success and the deleted tag's ID.
    """
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()

    return jsonify({
        'message': 'Tag deleted successfully',
        'tag_id': tag.id
    }), 200

@admin_bp.route('/admin/organizations', methods=['POST'])
def create_organization():
    """
    Creates a new organization.
    
    Expects a JSON payload with organization details.
    
    Returns:
        jsonify: A message indicating success and the created organization's ID.
    """
    data = request.get_json()
    organization = Organization(
        name=data['name'],
        description=data['description'],
        homepage_url=data['homepage_url']
    )
    db.session.add(organization)
    db.session.commit()

    return jsonify({
        'message': 'Organization created successfully',
        'organization_id': organization.id
    }), 201

@admin_bp.route('/admin/organizations/<int:organization_id>', methods=['PUT'])
def update_organization(organization_id):
    """
    Updates an existing organization.
    
    Expects a JSON payload with updated organization details.
    
    Args:
        organization_id (int): The ID of the organization to be updated.
        
    Returns:
        jsonify: A message indicating success and the updated organization's ID.
    """
    data = request.get_json()
    organization = Organization.query.get_or_404(organization_id)

    organization.name = data['name']
    organization.description = data['description']
    organization.homepage_url = data['homepage_url']

    db.session.commit()

    return jsonify({
        'message': 'Organization updated successfully',
        'organization_id': organization.id
    }), 200

@admin_bp.route('/admin/organizations/<int:organization_id>', methods=['DELETE'])
def delete_organization(organization_id):
    """
    Deletes an organization.
    
    Args:
        organization_id (int): The ID of the organization to be deleted.
        
    Returns:
        jsonify: A message indicating success and the deleted organization's ID.
    """
    organization = Organization.query.get_or_404(organization_id)
    db.session.delete(organization)
    db.session.commit()

    return jsonify({
        'message': 'Organization deleted successfully',
        'organization_id': organization.id
    }), 200

@admin_bp.route('/admin/bots', methods=['POST'])
def create_bot():
    """
    Creates a new bot.
    
    Expects a JSON payload with bot details.
    
    Returns:
        jsonify: A message indicating success and the created bot's ID.
    """
    data = request.get_json()
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

@admin_bp.route('/admin/bots/<int:bot_id>', methods=['PUT'])
def update_bot(bot_id):
    """
    Updates an existing bot.
    
    Expects a JSON payload with updated bot details.
    
    Args:
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

@admin_bp.route('/admin/bots/<int:bot_id>', methods=['DELETE'])
def delete_bot(bot_id):
    """
    Deletes a bot.
    
    Args:
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

@admin_bp.route('/admin/notifications', methods=['POST'])
def create_notification():
    """
    Creates a new notification.
    
    Expects a JSON payload with notification details.
    
    Returns:
        jsonify: A message indicating success and the created notification's ID.
    """
    data = request.get_json()
    notification = Notification(
        message=data['message'],
        type=data['type']
    )
    db.session.add(notification)
    db.session.commit()

    return jsonify({
        'message': 'Notification created successfully',
        'notification_id': notification.id
    }), 201

@admin_bp.route('/admin/notifications/<int:notification_id>', methods=['PUT'])
def update_notification(notification_id):
    """
    Updates an existing notification.
    
    Expects a JSON payload with updated notification details.
    
    Args:
        notification_id (int): The ID of the notification to be updated.
        
    Returns:
        jsonify: A message indicating success and the updated notification's ID.
    """
    data = request.get_json()
    notification = Notification.query.get_or_404(notification_id)

    notification.message = data['message']
    notification.type = data['type']

    db.session.commit()

    return jsonify({
        'message': 'Notification updated successfully',
        'notification_id': notification.id
    }), 200

@admin_bp.route('/admin/notifications/<int:notification_id>', methods=['DELETE'])
def delete_notification(notification_id):
    """
    Deletes a notification.
    
    Args:
        notification_id (int): The ID of the notification to be deleted.
        
    Returns:
        jsonify: A message indicating success and the deleted notification's ID.
    """
    notification = Notification.query.get_or_404(notification_id)
    db.session.delete(notification)
    db.session.commit()

    return jsonify({
        'message': 'Notification deleted successfully',
        'notification_id': notification.id
    }), 200
