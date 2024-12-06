from flask import Blueprint, render_template, request, redirect, url_for
from app.forms.admin_forms import BotForm
from app.services.bot_service import create_bot, get_bot_by_id, run_bot, get_all_bots, update_bot
from app.extensions import db
# AI: add docstrings to all functions, methods, and classes
admin_bot_bp = Blueprint('admin_bot', __name__)

@admin_bot_bp.route('/bots/create', methods=['GET', 'POST'])
def create():
    form = BotForm()
    if form.validate_on_submit():
        bot = create_bot(form.name.data, form.description.data, 'idle')
        return redirect(url_for('admin_bot.index'))
    return render_template('admin/bot_form.html', form=form)

@admin_bot_bp.route('/bots/delete/<int:id>', methods=['POST'])
def delete(id):
    bot = get_bot_by_id(id)
    if bot:
        db.session.delete(bot)
        db.session.commit()
        return redirect(url_for('admin_bot.index'))
    return "Bot not found", 404

@admin_bot_bp.route('/bots/', methods=['GET'])
def index():
    bots = get_all_bots()
    return render_template('admin/bot_dashboard.html', bots=bots)

@admin_bot_bp.route('/bots/run/<int:id>', methods=['POST'])
def run(id):
    bot = get_bot_by_id(id)
    if bot:
        run_bot(bot)
        return redirect(url_for('admin_bot.index'))
    return "Bot not found", 404

@admin_bot_bp.route('/bots/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    bot = get_bot_by_id(id)
    if not bot:
        return "Bot not found", 404
    form = BotForm(obj=bot)
    if form.validate_on_submit():
        update_bot(bot, form.data)
        return redirect(url_for('admin_bot.index'))
    return render_template('admin/bot_form.html', form=form)
