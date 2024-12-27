from flask import Blueprint, render_template, redirect, url_for, request, current_app, render_template_string
from flask_login import login_required
from app.forms.admin_forms import BotForm
from app.services.bot_service import get_bot_by_id, run_bot, get_all_bots, create_bot, update_bot, delete_bot
from app.extensions import db 
from app.utils import admin_required, flash_message, format_error_message
from app.constants import FLASH_MESSAGES, FLASH_CATEGORY_SUCCESS, FLASH_CATEGORY_ERROR

admin_bot_bp = Blueprint('bot', __name__, url_prefix='/bots')

@admin_bot_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    form = BotForm()
    if form.validate_on_submit():
        try:
            new_bot = create_bot(form.data)
            flash_message(FLASH_MESSAGES["CREATE_BOT_SUCCESS"], FLASH_CATEGORY_SUCCESS)
            return redirect(url_for('admin.bot.index'))
        except Exception as e:
            db.session.rollback()
            flash_message(f"{FLASH_MESSAGES['CREATE_BOT_ERROR']}{str(e)}", FLASH_CATEGORY_ERROR)
            current_app.logger.error(f"Failed to create bot: {e}")
            return render_template('admin/bots/create.html', form=form), 400
    else:  # Add this else block to handle invalid form data
        for field, errors in form.errors.items():
            for error in errors:
                flash_message(f"{field}: {error}", FLASH_CATEGORY_ERROR)
                current_app.logger.error(f"Flashing error: {field}: {error}")
        return render_template('admin/bots/create.html', form=form), 400

@admin_bot_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(id):
    bot = get_bot_by_id(id)
    if bot:
        try:
            delete_bot(bot)
            flash_message(FLASH_MESSAGES["DELETE_BOT_SUCCESS"], FLASH_CATEGORY_SUCCESS)
            current_app.logger.info(f"Flash message set: {FLASH_MESSAGES['DELETE_BOT_SUCCESS']}")
        except Exception as e:
            db.session.rollback()
            flash_message(f"{FLASH_MESSAGES['DELETE_BOT_ERROR']}{str(e)}", FLASH_CATEGORY_ERROR)
            current_app.logger.error(f"Failed to delete bot: {e}")
    else:
        flash_message(FLASH_MESSAGES["BOT_NOT_FOUND"], FLASH_CATEGORY_ERROR)  # Use specific bot not found message
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
            flash_message(FLASH_MESSAGES["GENERIC_SUCCESS"], FLASH_CATEGORY_SUCCESS)  # Use generic success message for running a bot
            current_app.logger.info(f"Flash message set: {FLASH_MESSAGES['GENERIC_SUCCESS']}")
        except Exception as e:
            db.session.rollback()
            flash_message(f"{FLASH_MESSAGES['GENERIC_ERROR']}{str(e)}", FLASH_CATEGORY_ERROR)
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
        flash_message(FLASH_MESSAGES["BOT_NOT_FOUND"], FLASH_CATEGORY_ERROR)
        current_app.logger.error(f"Bot not found with id: {id}")
        return redirect(url_for('admin.bot.index'))
    
    form = BotForm(obj=bot)
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                update_bot(bot, form.data)
                flash_message(FLASH_MESSAGES["UPDATE_BOT_SUCCESS"], FLASH_CATEGORY_SUCCESS)
                current_app.logger.info(f"Flash message set: {FLASH_MESSAGES['UPDATE_BOT_SUCCESS']}")
                return redirect(url_for('admin.bot.index'))
            except Exception as e:
                db.session.rollback()
                flash_message(f"{FLASH_MESSAGES['UPDATE_BOT_ERROR']}{str(e)}", FLASH_CATEGORY_ERROR)
                current_app.logger.error(f"Failed to update bot: {e}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash_message(f"{field}: {error}", FLASH_CATEGORY_ERROR)
                    current_app.logger.error(f"Flashing error: {field}: {error}")

    return render_template('admin/bots/edit.html', form=form, bot=bot)
