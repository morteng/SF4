from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.services.bot_service import get_bot_by_id, update_bot_status

bot_bp = Blueprint('admin_bot', __name__)

@bot_bp.route('/bots')
@login_required
def list_bots():
    # Your code here
    pass

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
    if update_bot_status(bot_id, status):
        flash('Bot status updated successfully', 'success')
    else:
        flash('Failed to update bot status', 'danger')
    return redirect(url_for('admin_bot.bot_details', bot_id=bot_id))

# Add other routes as needed
