from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.services.bot_service import list_all_bots, get_bot_by_id, update_bot

bot_bp = Blueprint('bot', __name__, url_prefix='/bots')

@bot_bp.route('/', methods=['GET'])
@login_required
def list_bots():
    bots = list_all_bots()
    return render_template('admin/bot_list.html', bots=bots)

@bot_bp.route('/<int:bot_id>', methods=['GET'])
@login_required
def bot_details(bot_id):
    bot = get_bot_by_id(bot_id)
    if not bot:
        flash('Bot not found', 'danger')
        return redirect(url_for('bot.list_bots'))
    return render_template('admin/bot_details.html', bot=bot)

@bot_bp.route('/<int:bot_id>/update', methods=['POST'])
@login_required
def update_bot_route(bot_id):
    name = request.form.get('name')
    description = request.form.get('description')
    status = request.form.get('status')
    if update_bot(bot_id, name, description, status):
        flash('Bot updated successfully', 'success')
    else:
        flash('Failed to update bot', 'danger')
    return redirect(url_for('bot.bot_details', bot_id=bot_id))
