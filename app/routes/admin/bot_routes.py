from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from app.forms.admin_forms import BotForm
from app.services.bot_service import get_bot_by_id, run_bot, get_all_bots, create_bot, update_bot
from app.extensions import db  # Import the db object

# Define the bot blueprint without '/admin' in url_prefix
admin_bot_bp = Blueprint('admin_bot', __name__, url_prefix='/bots')

@admin_bot_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    """Delete a bot by ID."""
    bot = get_bot_by_id(id)
    if bot:
        db.session.delete(bot)
        db.session.commit()
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

@admin_bot_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = BotForm()
    if form.validate_on_submit():
        new_bot = create_bot(form.data)
        flash('Bot created successfully.', 'success')
        return redirect(url_for('admin_bot.index'))
    return render_template('admin/bot/create.html', form=form)

@admin_bot_bp.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    bot = get_bot_by_id(id)
    if not bot:
        flash('Bot not found.', 'danger')
        return redirect(url_for('admin_bot.index'))
    form = BotForm(obj=bot)
    if form.validate_on_submit():
        update_bot(bot, form.data)
        flash('Bot updated successfully.', 'success')
        return redirect(url_for('admin_bot.index'))
    return render_template('admin/bot/update.html', form=form, bot=bot)
