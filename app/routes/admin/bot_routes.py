from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.forms.admin_forms import BotForm
from app.services.bot_service import get_bot_by_id, run_bot, get_all_bots, create_bot, update_bot, delete_bot

admin_bot_bp = Blueprint('bot', __name__, url_prefix='/bots')

@bot.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = BotForm()
    if form.validate_on_submit():
        new_bot = create_bot(form.data)
        flash('Bot created successfully.', 'success')
        return redirect(url_for('admin.bot.index'))
    return render_template('admin/bot/create.html', form=form)

@bot.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    bot = get_bot_by_id(id)
    if bot:
        delete_bot(bot)
        flash(f'Bot {bot.name} deleted.', 'success')
    else:
        flash('Bot not found.', 'danger')
    return redirect(url_for('admin.bot.index'))

@bot.route('/', methods=['GET'])
@login_required
def index():
    bots = get_all_bots()
    return render_template('admin/bot/index.html', bots=bots)

@bot.route('/<int:id>/run', methods=['POST'])
@login_required
def run(id):
    bot = get_bot_by_id(id)
    if bot:
        run_bot(bot)
        flash(f'Bot {bot.name} started running.', 'success')
    else:
        flash('Bot not found.', 'danger')
    return redirect(url_for('admin.bot.index'))

@bot.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    bot = get_bot_by_id(id)
    if not bot:
        flash('Bot not found.', 'danger')
        return redirect(url_for('admin.bot.index'))
    form = BotForm(obj=bot)
    if form.validate_on_submit():
        update_bot(bot, form.data)
        flash('Bot updated successfully.', 'success')
        return redirect(url_for('admin.bot.index'))
    return render_template('admin/bot/update.html', form=form, bot=bot)
