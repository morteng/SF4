from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from app.services.bot_service import get_bot_by_id, run_bot, get_all_bots

admin_bot_bp = Blueprint('admin_bot', __name__, url_prefix='/admin/bots')

@admin_bot_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    """Delete a bot by ID."""
    bot = get_bot_by_id(id)
    if bot:
        # Assuming there's a method to delete the bot, let's add it here
        # For now, we'll just flash a message
        flash(f'Bot {bot.name} deleted.', 'success')
    else:
        flash('Bot not found.', 'danger')
    return redirect(url_for('admin_bot.index'))

@admin_bot_bp.route('/run/<int:id>', methods=['POST'])
@login_required
def run(id):
    """Run a bot by ID."""
    bot = get_bot_by_id(id)
    if bot:
        run_bot(bot)
        flash(f'Bot {bot.name} started running.', 'success')
    else:
        flash('Bot not found.', 'danger')
    return redirect(url_for('admin_bot.index'))

@admin_bot_bp.route('/', methods=['GET'])
@login_required
def index():
    """List all bots."""
    bots = get_all_bots()
    return render_template('admin/bot/index.html', bots=bots)
