from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.forms.admin_forms import BotForm
from app.services.bot_service import get_bot_by_id, run_bot, get_all_bots, create_bot, update_bot, delete_bot

admin_bot_bp = Blueprint('bot', __name__, url_prefix='/bots')

@admin_bot_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = BotForm()
    if form.validate_on_submit():
        try:
            new_bot = create_bot(form.data)
            flash('Bot created successfully.', 'success')
            return redirect(url_for('admin.bot.index'))
        except Exception as e:
            db.session.rollback()  # Ensure the session is rolled back on error
            flash('Failed to create bot.', 'danger')
            return render_template('admin/bots/create.html', form=form), 200
    return render_template('admin/bots/create.html', form=form)

@admin_bot_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    bot = get_bot_by_id(id)
    if bot:
        delete_bot(bot)
        flash(f'Bot {bot.name} deleted.', 'success')
    else:
        flash('Bot not found.', 'danger')
    return redirect(url_for('admin.bot.index'))

@admin_bot_bp.route('/', methods=['GET'])
@login_required
def index():
    bots = get_all_bots()
    return render_template('admin/bots/index.html', bots=bots)

@admin_bot_bp.route('/<int:id>/run', methods=['POST'])
@login_required
def run(id):
    bot = get_bot_by_id(id)
    if bot:
        run_bot(bot)
        flash(f'Bot {bot.name} started.', 'success')
    else:
        flash('Bot not found.', 'danger')
    return redirect(url_for('admin.bot.index'))

@admin_bot_bp.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    bot = get_bot_by_id(id)
    if not bot:
        flash('Bot not found.', 'danger')
        return redirect(url_for('admin.bot.index'))
    
    form = BotForm(obj=bot)
    if request.method == 'POST' and form.validate_on_submit():
        update_bot(bot, form.data)
        flash('Bot updated successfully.', 'success')
        return redirect(url_for('admin.bot.index'))
    
    return render_template('admin/bots/_edit_row.html', form=form, bot=bot)
