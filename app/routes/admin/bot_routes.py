from flask import Blueprint, redirect, url_for, flash, render_template
from flask_login import login_required
from app.models.bot import Bot
from app.services.bot_service import get_bot_by_id, run_bot

admin_bot_bp = Blueprint('admin_bot', __name__, url_prefix='/admin/bots')

@admin_bot_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    bot = get_bot_by_id(id)
    if bot:
        db.session.delete(bot)
        db.session.commit()
        flash('Bot deleted successfully.', 'success')
    else:
        flash('Bot not found.', 'danger')
    return redirect(url_for('admin_bot.index'))

@admin_bot_bp.route('/run/<int:id>', methods=['POST'])
@login_required
def run(id):
    bot = get_bot_by_id(id)
    if bot:
        run_bot(bot)
        flash('Bot started successfully.', 'success')
    else:
        flash('Bot not found.', 'danger')
    return redirect(url_for('admin_bot.index'))
