from datetime import datetime, timezone
import time
from flask import (
    Blueprint, render_template, request, redirect, 
    url_for, jsonify, current_app, flash
)
from flask_login import login_required, current_user
from app.controllers.admin_base_controller import AdminBaseController
from app.forms.admin_forms import BotForm
from app.services.bot_service import BotService
from app.models.audit_log import AuditLog
from app.extensions import db
from app.utils import calculate_next_run
from app.constants import FlashMessages, FlashCategory

admin_bot_bp = Blueprint('bot_admin', __name__, url_prefix='/admin/bots')

bot_controller = AdminBaseController(
    service=BotService(),
    entity_name='bot',
    form_class=BotForm,
    template_dir='bots'
)
bot_controller._register_routes()

@admin_bot_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    return bot_controller.delete(id)

@admin_bot_bp.route('/<int:id>/run', methods=['POST'])
@login_required
def run(id):
    """Run bot with status tracking and notifications"""
    bot_service = BotService()
    bot = bot_service.get_by_id(id)
    if not bot:
        flash(FlashMessages.BOT_NOT_FOUND.value, FlashCategory.ERROR.value)
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
        
        flash(f"Bot {bot.name} completed successfully", FlashCategory.SUCCESS.value)
    except Exception as e:
        db.session.rollback()
        bot.status = 'error'
        bot.error_log = str(e)
        db.session.commit()
        flash(f"Failed to run bot: {str(e)}", FlashCategory.ERROR.value)
        
    return redirect(url_for('admin.bot.index'))

@admin_bot_bp.route('/<int:id>/schedule', methods=['POST'])
@login_required
def schedule(id):
    bot_service = BotService()
    bot = bot_service.get_by_id(id)
    if not bot:
        flash(FlashMessages.BOT_NOT_FOUND.value, FlashCategory.ERROR.value)
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
        
        flash(FlashMessages.BOT_SCHEDULED_SUCCESS.value, FlashCategory.SUCCESS.value)
        return jsonify({"status": "success"})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to schedule bot {bot.name}: {e}")
        flash(f"Failed to schedule bot: {str(e)}", FlashCategory.ERROR.value)
        return jsonify({"status": "error", "message": str(e)}), 400

@admin_bot_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    if request.method == 'POST':
        form = BotForm(request.form)
        if form.validate():
            return bot_controller.edit(id, form.data)
    else:
        bot_service = BotService()
        bot = bot_service.get_by_id(id)
        form = BotForm(obj=bot)
    return render_template('admin/bots/edit.html', form=form, bot=bot)
