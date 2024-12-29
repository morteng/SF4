from datetime import datetime, timezone
import time
from flask import Blueprint, render_template, redirect, url_for, request, jsonify, current_app
from flask_login import login_required, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.models.bot import Bot
from app.models.audit_log import AuditLog
from app.forms.admin_forms import BotForm
from app.extensions import db
from app.utils import (
    admin_required, 
    flash_message, 
    calculate_next_run,
    log_audit,
    create_notification
)
from app.constants import FlashMessages, FlashCategory
from app.services.bot_service import BotService

admin_bot_bp = Blueprint('bot', __name__, url_prefix='/bots')

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per hour", "10 per minute"]
)

@admin_bot_bp.route('/create', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
@login_required
@admin_required
def create():
    """Create a new bot with audit logging and notifications"""
    form = BotForm()
    is_htmx = request.headers.get('HX-Request')
    
    if form.validate_on_submit():
        try:
            bot_data = {
                'name': form.name.data,
                'description': form.description.data,
                'status': 'inactive',
                'schedule': form.schedule.data,
                'last_run': None
            }
            
            # Create bot
            bot_service = BotService()
            new_bot = bot_service.create(bot_data)
            
            # Create audit log
            log_audit(
                user_id=current_user.id,
                action='create_bot',
                object_type='Bot',
                object_id=new_bot.id,
                after=new_bot.to_dict()
            )
            
            # Create notification
            create_notification(
                type='crud',
                message=f'Bot {new_bot.name} created',
                related_object=new_bot,
                user_id=current_user.id
            )
            
            flash_message(FlashMessages.BOT_CREATE_SUCCESS, FlashCategory.SUCCESS)
            
            if is_htmx:
                return render_template('admin/bots/_bot_row.html', bot=new_bot), 200, {
                    'HX-Trigger': 'botCreated'
                }
            return redirect(url_for('admin.bot.index'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating bot: {str(e)}")
            flash_message(f"{FlashMessages.BOT_CREATE_ERROR}: {str(e)}", FlashCategory.ERROR)
            if is_htmx:
                return render_template('admin/bots/_form.html', form=form), 400
    
    return render_template('admin/bots/create.html', form=form)

@admin_bot_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(id):
    bot_service = BotService()
    bot = bot_service.get_by_id(id)
    if bot:
        try:
            bot_service.delete(bot)
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
    bot_service = BotService()
    bots = bot_service.get_all()
    return render_template('admin/bots/index.html', bots=bots)

@admin_bot_bp.route('/<int:id>/run', methods=['POST'])
@limiter.limit("10 per hour")
@login_required
@admin_required
def run(id):
    """Run bot with status tracking and notifications"""
    bot_service = BotService()
    bot = bot_service.get_by_id(id)
    if not bot:
        flash_message(FlashMessages.BOT_NOT_FOUND, FlashCategory.ERROR)
        return redirect(url_for('admin.bot.index'))

    try:
        # Update bot status
        bot.status = 'running'
        bot.last_run = datetime.now(timezone.utc)
        bot.error_log = None
        db.session.commit()
        
        # Simulate bot running
        time.sleep(2)  # Simulate processing time
        bot.status = 'completed'
        db.session.commit()
        
        flash_message(f"Bot {bot.name} completed successfully", FlashCategory.SUCCESS)
    except Exception as e:
        db.session.rollback()
        bot.status = 'error'
        bot.error_log = str(e)
        db.session.commit()
        flash_message(f"Failed to run bot: {str(e)}", FlashCategory.ERROR)
        
    return redirect(url_for('admin.bot.index'))

@admin_bot_bp.route('/<int:id>/schedule', methods=['POST'])
@login_required
@admin_required
def schedule(id):
    bot_service = BotService()
    bot = bot_service.get_by_id(id)
    if not bot:
        flash_message(FlashMessages.BOT_NOT_FOUND.value, FlashCategory.ERROR.value)
        return redirect(url_for('admin.bot.index'))

    try:
        schedule_data = request.get_json()
        if not schedule_data or 'schedule' not in schedule_data:
            raise ValueError("Invalid schedule data")
            
        bot.schedule = schedule_data['schedule']
        bot.next_run = calculate_next_run(schedule_data['schedule'])
        db.session.commit()
        
        # Create audit log
        AuditLog.create(
            user_id=current_user.id,
            action='schedule_bot',
            object_type='Bot',
            object_id=bot.id,
            details=f"Scheduled {bot.name} with {schedule_data['schedule']}",
            ip_address=request.remote_addr
        )
        
        flash_message(FlashMessages.BOT_SCHEDULED_SUCCESS.value, FlashCategory.SUCCESS)
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
    bot_service = BotService()
    bot = bot_service.get_by_id(id)
    if not bot:
        flash_message(FlashMessages.BOT_NOT_FOUND.value, FlashCategory.ERROR.value)
        current_app.logger.error(f"Bot not found with id: {id}")
        return redirect(url_for('admin.bot.index'))
    
    form = BotForm(obj=bot)
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                bot_service = BotService()
                bot_service.update(bot, form.data)
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
