from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, current_app, render_template_string, get_flashed_messages, jsonify
from flask_login import login_required
from app.models.notification import Notification, NotificationType
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
            
            # Create audit log
            AuditLog.create(
                user_id=current_user.id,
                action='create_bot',
                object_type='Bot',
                object_id=new_bot.id,
                details=f'Created bot {new_bot.name}',
                ip_address=request.remote_addr
            )
            
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
@limiter.limit("10 per hour")
@login_required
@admin_required
def run(id):
    """Run bot with status tracking and notifications"""
    bot = get_bot_by_id(id)
    if not bot:
        flash_message(FlashMessages.BOT_NOT_FOUND.value, FlashCategory.ERROR.value)
        return redirect(url_for('admin.bot.index'))

    try:
        # Run the appropriate bot based on name
        if bot.name == 'TagBot':
            from bots.tag_bot import TagBot
            result = TagBot().run()
        elif bot.name == 'UpdateBot':
            from bots.update_bot import UpdateBot
            result = UpdateBot().run()
        elif bot.name == 'ReviewBot':
            from bots.review_bot import ReviewBot
            result = ReviewBot().run()
        else:
            raise ValueError("Unknown bot type")
        
        # Update bot status and last run time
        bot.status = result['status']
        bot.last_run = datetime.utcnow()
        
        # Create appropriate notification
        notification_type = NotificationType.BOT_SUCCESS if result['success'] else NotificationType.BOT_ERROR
        notification = Notification(
            message=f"Bot {bot.name} run completed: {result['message']}",
            type=notification_type,
            read_status=False
        )
        
        # Add error notification if bot failed
        if not result['success']:
            current_app.logger.error(f"Bot {bot.name} failed: {result['message']}")
        
        db.session.add(notification)
        db.session.commit()
        
        flash_message(result['message'], FlashCategory.SUCCESS if result['success'] else FlashCategory.ERROR)
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to run bot {bot.name}: {e}")
        flash_message(f"Failed to run bot: {str(e)}", FlashCategory.ERROR)
        
    return redirect(url_for('admin.bot.index'))

@admin_bot_bp.route('/<int:id>/schedule', methods=['POST'])
@login_required
@admin_required
def schedule(id):
    bot = get_bot_by_id(id)
    if not bot:
        flash_message(FlashMessages.BOT_NOT_FOUND.value, FlashCategory.ERROR.value)
        return redirect(url_for('admin.bot.index'))

    try:
        schedule_data = request.get_json()
        if not schedule_data or 'schedule' not in schedule_data:
            raise ValueError("Invalid schedule data")
            
        bot.schedule = schedule_data['schedule']
        db.session.commit()
        
        flash_message(f"Bot {bot.name} scheduled successfully", FlashCategory.SUCCESS)
        return jsonify({"status": "success"})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to schedule bot {bot.name}: {e}")
        flash_message(f"Failed to schedule bot: {str(e)}", FlashCategory.ERROR)
        return jsonify({"status": "error", "message": str(e)}), 400

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
