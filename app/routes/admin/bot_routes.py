from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required
from app.forms.admin_forms import BotForm
from app.services.bot_service import get_bot_by_id, run_bot, get_all_bots, create_bot, update_bot, delete_bot
from app.extensions import db 
from app.utils import admin_required, flash_message

admin_bot_bp = Blueprint('bot', __name__, url_prefix='/bots')

@admin_bot_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    form = BotForm()
    if form.validate_on_submit():
        try:
            new_bot = create_bot(form.data)
            flash_message("Bot created successfully", "success")
            return redirect(url_for('admin.bot.index'))
        except Exception as e:
            db.session.rollback()  # Ensure the session is rolled back on error
            flash_message(f"Failed to create bot: {str(e)}", "error")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash_message(f"{field}: {error}", "error")
        if not form.validate_on_submit():
            flash_message("Invalid data provided", "error")  # Use specific invalid data message
    return render_template('admin/bots/create.html', form=form)

@admin_bot_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(id):
    bot = get_bot_by_id(id)
    if bot:
        try:
            delete_bot(bot)
            flash_message("Bot deleted successfully", "success")
        except Exception as e:
            db.session.rollback()
            flash_message(f"Failed to delete bot: {str(e)}", "error")
    else:
        flash_message("Bot not found", "error")  # Use specific bot not found message
    return redirect(url_for('admin.bot.index'))

@admin_bot_bp.route('/', methods=['GET'])
@login_required
@admin_required
def index():
    bots = get_all_bots()
    return render_template('admin/bots/index.html', bots=bots)

@admin_bot_bp.route('/<int:id>/run', methods=['POST'])
@login_required
@admin_required
def run(id):
    bot = get_bot_by_id(id)
    if bot:
        try:
            run_bot(bot)
            flash_message("Bot run successfully", "success")
        except Exception as e:
            db.session.rollback()
            flash_message(f"Failed to run bot: {str(e)}", "error")
    else:
        flash_message("Bot not found", "error")  # Use specific bot not found message
    return redirect(url_for('admin.bot.index'))

@admin_bot_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    bot = get_bot_by_id(id)
    if not bot:
        flash_message("Bot not found", "error")  # Use specific bot not found message
        return redirect(url_for('admin.bot.index'))
    
    form = BotForm(obj=bot)
    if request.method == 'POST' and form.validate_on_submit():
        try:
            update_bot(bot, form.data)
            flash_message("Bot updated successfully", "success")
        except Exception as e:
            db.session.rollback()
            flash_message(f"Failed to update bot: {str(e)}", "error")
        return redirect(url_for('admin.bot.index'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash_message(f"{field}: {error}", "error")

    return render_template('admin/bots/_edit_row.html', form=form, bot=bot)
