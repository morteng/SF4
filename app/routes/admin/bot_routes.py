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
            db.session.rollback()  # Ensure the session is rolled back on error
            flash_message(f"{FLASH_MESSAGES['CREATE_BOT_ERROR']}{str(e)}", FLASH_CATEGORY_ERROR)
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash_message(f"{field}: {error}", FLASH_CATEGORY_ERROR)
        if not form.validate_on_submit():
            flash_message(FLASH_MESSAGES["CREATE_BOT_INVALID_DATA"], FLASH_CATEGORY_ERROR)  # Use specific invalid data message
    return render_template('admin/bots/create.html', form=form)

@admin_bot_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(id):
    bot = get_bot_by_id(id)
    if bot:
        try:
            delete_bot(bot)
            flash_message(FLASH_MESSAGES["DELETE_BOT_SUCCESS"], FLASH_CATEGORY_SUCCESS)
        except Exception as e:
            db.session.rollback()
            flash_message(f"{FLASH_MESSAGES['DELETE_BOT_ERROR']}{str(e)}", FLASH_CATEGORY_ERROR)
    else:
        flash_message(FLASH_MESSAGES["BOT_NOT_FOUND"], FLASH_CATEGORY_ERROR)  # Use specific bot not found message
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
            flash_message(FLASH_MESSAGES["RUN_BOT_SUCCESS"], FLASH_CATEGORY_SUCCESS)
        except Exception as e:
            db.session.rollback()
            flash_message(f"{FLASH_MESSAGES['RUN_BOT_ERROR']}{str(e)}", FLASH_CATEGORY_ERROR)
    else:
        flash_message(FLASH_MESSAGES["BOT_NOT_FOUND"], FLASH_CATEGORY_ERROR)  # Use specific bot not found message
    return redirect(url_for('admin.bot.index'))

@admin_bot_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    bot = get_bot_by_id(id)
    if not bot:
        flash_message(FLASH_MESSAGES["BOT_NOT_FOUND"], FLASH_CATEGORY_ERROR)  # Use specific bot not found message
        return redirect(url_for('admin.bot.index'))
    
    form = BotForm(obj=bot)
    if request.method == 'POST' and form.validate_on_submit():
        try:
            update_bot(bot, form.data)
            flash_message(FLASH_MESSAGES["UPDATE_BOT_SUCCESS"], FLASH_CATEGORY_SUCCESS)
        except Exception as e:
            db.session.rollback()
            flash_message(f"{FLASH_MESSAGES['UPDATE_BOT_ERROR']}{str(e)}", FLASH_CATEGORY_ERROR)
        return redirect(url_for('admin.bot.index'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash_message(f"{field}: {error}", FLASH_CATEGORY_ERROR)

    return render_template('admin/bots/_edit_row.html', form=form, bot=bot)
