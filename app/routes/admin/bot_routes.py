from flask import Blueprint, request, jsonify, redirect, url_for, flash, render_template
from flask_login import login_required
from app.services.bot_service import get_bot_by_id, update_bot_status, create_bot, list_all_bots

bot_bp = Blueprint('admin_bot', __name__)

@bot_bp.route('/bots')
@login_required
def list_bots():
    bots = list_all_bots()
    return render_template('admin/bot_list.html', bots=bots)

@bot_bp.route('/bots/<int:bot_id>')
@login_required
def bot_details(bot_id):
    bot = get_bot_by_id(bot_id)
    if not bot:
        flash('Bot not found', 'danger')
        return redirect(url_for('admin_bot.list_bots'))
    return render_template('admin/bot_details.html', bot=bot)

@bot_bp.route('/bots/<int:bot_id>/update_status', methods=['POST'])
@login_required
def update_bot(bot_id):
    status = request.form.get('status')
    if not status:
        flash('Status is required', 'danger')
        return redirect(url_for('admin_bot.bot_details', bot_id=bot_id))
    
    if update_bot_status(bot_id, status):
        flash('Bot status updated successfully', 'success')
    else:
        flash('Failed to update bot status', 'danger')
    return redirect(url_for('admin_bot.bot_details', bot_id=bot_id))

@bot_bp.route('/bots', methods=['POST'])
@login_required
def create_bot():
    name = request.form.get('name')
    description = request.form.get('description')
    status = request.form.get('status')

    if not name or not description or not status:
        flash('Missing required fields', 'danger')
        return redirect(url_for('admin_bot.list_bots'))

    bot = create_bot(name, description, status)
    if bot:
        flash('Bot created successfully', 'success')
        return redirect(url_for('admin_bot.bot_details', bot_id=bot.id))
    else:
        flash('Failed to create bot', 'danger')
        return redirect(url_for('admin_bot.list_bots'))

# Add API endpoint for creating bots
@bot_bp.route('/api/bots', methods=['POST'])
@login_required
def api_create_bot():
    name = request.json.get('name')
    description = request.json.get('description')
    status = request.json.get('status')

    if not name or not description or not status:
        return jsonify({"message": "Missing required fields"}), 400

    bot = create_bot(name, description, status)
    if bot:
        return jsonify({"bot_id": bot.id}), 201
    else:
        return jsonify({"message": "Failed to create bot"}), 500
