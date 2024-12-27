from flask import Blueprint, render_template, redirect, url_for, request, current_app, render_template_string, get_flashed_messages
from flask_login import login_required
from app.forms.admin_forms import BotForm
from app.services.bot_service import get_bot_by_id, run_bot, get_all_bots, create_bot, update_bot, delete_bot
from app.extensions import db 
from app.utils import admin_required, flash_message, format_error_message
from app.constants import FlashMessages, FlashCategory

admin_bot_bp = Blueprint('bot', __name__, url_prefix='/bots')

@admin_bot_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    form = BotForm()
    if form.validate_on_submit():
        try:
            new_bot = create_bot(form.data)
            flash_message(FlashMessages.CREATE_BOT_SUCCESS.value, FlashCategory.SUCCESS.value)
            return redirect(url_for('admin.bot.index'))
        except Exception as e:
            db.session.rollback()
            flash_message(f"{FlashMessages.CREATE_BOT_ERROR.value}{str(e)}", FlashCategory.ERROR.value)
            current_app.logger.error(f"Failed to create bot: {e}")
            return render_template('admin/bots/create.html', form=form), 400
    elif request.method == 'POST':
        # Enhanced error handling
        for field, errors in form.errors.items():
            for error in errors:
                flash_message(f"{field}: {error}", FlashCategory.ERROR.value)
                current_app.logger.error(f"Form validation error - {field}: {error}")
        flash_message(FlashMessages.CREATE_BOT_INVALID_DATA.value, FlashCategory.ERROR.value)
        current_app.logger.error("Invalid form data submitted for bot creation")
        return render_template('admin/bots/create.html', form=form, flash_messages=get_flashed_messages()), 400
    return render_template('admin/bots/create.html', form=form)

@admin_bot_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(id):
    bot = get_bot_by_id(id)
    if bot:
        try:
            delete_bot(bot)
            flash_message(FlashMessages.DELETE_BOT_SUCCESS.value, FlashCategory.SUCCESS.value)
            current_app.logger.info(f"Flash message set: {FlashMessages.DELETE_BOT_SUCCESS.value}")
        except Exception as e:
            db.session.rollback()
            flash_message(f"{FlashMessages.DELETE_BOT_ERROR.value}{str(e)}", FlashCategory.ERROR.value)
            current_app.logger.error(f"Failed to delete bot: {e}")
    else:
        flash_message(FlashMessages.BOT_NOT_FOUND.value, FlashCategory.ERROR.value)  # Use specific bot not found message
        current_app.logger.error(f"Bot not found with id: {id}")
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
            flash_message(FlashMessages.GENERIC_SUCCESS.value, FlashCategory.SUCCESS.value)  # Use generic success message for running a bot
            current_app.logger.info(f"Flash message set: {FlashMessages.GENERIC_SUCCESS.value}")
        except Exception as e:
            db.session.rollback()
            flash_message(f"{FlashMessages.GENERIC_ERROR.value}{str(e)}", FlashCategory.ERROR.value)
            current_app.logger.error(f"Failed to run bot: {e}")
    else:
        flash_message(FLASH_MESSAGES["BOT_NOT_FOUND"], FLASH_CATEGORY_ERROR)  # Use specific bot not found message
        current_app.logger.error(f"Bot not found with id: {id}")
    return redirect(url_for('admin.bot.index'))

@admin_bot_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    bot = get_bot_by_id(id)
    if not bot:
        flash_message(FlashMessages.BOT_NOT_FOUND.value, FlashCategory.ERROR.value)
        current_app.logger.error(f"Bot not found with id: {id}")
        return redirect(url_for('admin.bot.index'))
    
    form = BotForm(obj=bot)
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                update_bot(bot, form.data)
                flash_message(FlashMessages.UPDATE_BOT_SUCCESS.value, FlashCategory.SUCCESS.value)
                current_app.logger.info(f"Flash message set: {FlashMessages.UPDATE_BOT_SUCCESS.value}")
                return redirect(url_for('admin.bot.index'))
            except Exception as e:
                db.session.rollback()
                flash_message(f"{FlashMessages.UPDATE_BOT_ERROR.value}{str(e)}", FlashCategory.ERROR.value)
                current_app.logger.error(f"Failed to update bot: {e}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash_message(f"{field}: {error}", FlashCategory.ERROR.value)
                    current_app.logger.error(f"Flashing error: {field}: {error}")

    return render_template('admin/bots/edit.html', form=form, bot=bot)
