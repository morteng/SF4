# app/routes/admin/bot_routes.py

from flask_sqlalchemy import SQLAlchemy
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from app.models.bot import Bot
from app.forms.admin_forms import BotForm
from app.services.bot_service import BotService
from app.utils import admin_required

db = SQLAlchemy()

admin_bot_bp = Blueprint('admin_bot', __name__, url_prefix='/admin/bots')

@admin_bot_bp.route('/')
@admin_required
def index():
    bots = Bot.query.all()
    return render_template('admin/bots/index.html', bots=bots)

@admin_bot_bp.route('/run/<int:id>', methods=['POST'])
@admin_required
def run_bot(id):
    bot = Bot.query.get_or_404(id)
    try:
        BotService.run_bot(bot.name)
        flash(f'{bot.name} executed successfully.', 'success')
    except Exception as e:
        flash(f'Error running {bot.name}: {str(e)}', 'danger')
    return redirect(url_for('admin_bot.index'))

@admin_bot_bp.route('/logs/<int:id>')
@admin_required
def view_logs(id):
    bot = Bot.query.get_or_404(id)
    logs = bot.error_log
    return render_template('admin/bots/logs.html', bot=bot, logs=logs)
