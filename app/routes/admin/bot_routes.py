from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models.bot import Bot
from app.forms.admin_forms import BotForm
from app.services.bot_service import get_bot_by_id, run_bot
from app import db

admin_bot_bp = Blueprint('admin_bot', __name__, url_prefix='/admin/bots')

@admin_bot_bp.route('/')
@login_required
def index():
    bots = Bot.query.all()
    return render_template('admin/bot_index.html', bots=bots)

@admin_bot_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = BotForm()
    if form.validate_on_submit():
        bot = Bot(
            name=form.name.data,
            description=form.description.data,
            status='inactive'
        )
        db.session.add(bot)
        db.session.commit()
        flash('Bot created successfully!', 'success')
        return redirect(url_for('admin_bot.index'))
    return render_template('admin/bot_form.html', form=form, title='Create Bot')

@admin_bot_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    bot = get_bot_by_id(id)
    if not bot:
        flash('Bot not found!', 'danger')
        return redirect(url_for('admin_bot.index'))
    
    form = BotForm(obj=bot)
    if form.validate_on_submit():
        bot.name = form.name.data
        bot.description = form.description.data
        db.session.commit()
        flash('Bot updated successfully!', 'success')
        return redirect(url_for('admin_bot.index'))
    return render_template('admin/bot_form.html', form=form, title='Edit Bot')

@admin_bot_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    bot = get_bot_by_id(id)
    if not bot:
        flash('Bot not found!', 'danger')
        return redirect(url_for('admin_bot.index'))
    
    db.session.delete(bot)
    db.session.commit()
    flash('Bot deleted successfully!', 'success')
    return redirect(url_for('admin_bot.index'))

@admin_bot_bp.route('/run/<int:id>', methods=['POST'])
@login_required
def run(id):
    bot = get_bot_by_id(id)
    if not bot:
        flash('Bot not found!', 'danger')
        return redirect(url_for('admin_bot.index'))
    
    try:
        run_bot(bot)
        flash('Bot started successfully!', 'success')
    except Exception as e:
        flash(f'Failed to start bot: {str(e)}', 'danger')
    
    return redirect(url_for('admin_bot.index'))
