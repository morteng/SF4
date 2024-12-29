from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from app.controllers.base_crud_controller import BaseCrudController
from app.forms.admin_forms import BotForm
from app.services.bot_service import BotService
from app.constants import FlashMessages, FlashCategory

admin_bot_bp = Blueprint('bot', __name__, url_prefix='/bots')

bot_controller = BaseCrudController(
    service=BotService(),
    entity_name='bot',
    form_class=BotForm
)

@admin_bot_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        form = BotForm(request.form)
        if form.validate():
            return bot_controller.create(form.data)
    else:
        form = BotForm()
    return render_template('admin/bots/create.html', form=form)

@admin_bot_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    return bot_controller.delete(id)

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
