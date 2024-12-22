@admin_tag_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    form = TagForm()
    if form.validate_on_submit():
        try:
            new_tag = create_tag(form.data)
            if new_tag is None:
                flash_message(FLASH_MESSAGES["CREATE_TAG_ERROR"], FLASH_CATEGORY_ERROR)
                return render_template('admin/tags/create.html', form=form)
            flash_message(FLASH_MESSAGES["CREATE_TAG_SUCCESS"], FLASH_CATEGORY_SUCCESS)
            return redirect(url_for('admin.tag.index'))
        except IntegrityError as e:
            db.session.rollback()
            flash_message(FLASH_MESSAGES["CREATE_TAG_ERROR"], FLASH_CATEGORY_ERROR)
            return render_template('admin/tags/create.html', form=form)
        except Exception as e:
            db.session.rollback()
            flash_message(FLASH_MESSAGES["CREATE_TAG_ERROR"], FLASH_CATEGORY_ERROR)
            return render_template('admin/tags/create.html', form=form)
    return render_template('admin/tags/create.html', form=form)

@admin_tag_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(id):
    tag = get_tag_by_id(id)
    if tag:
        try:
            delete_tag(tag)
            flash_message(FLASH_MESSAGES["DELETE_TAG_SUCCESS"], FLASH_CATEGORY_SUCCESS)
        except Exception as e:
            db.session.rollback()
            flash_message(FLASH_MESSAGES["DELETE_TAG_ERROR"], FLASH_CATEGORY_ERROR)
    else:
        flash_message(FLASH_MESSAGES["GENERIC_ERROR"], FLASH_CATEGORY_ERROR)
    return redirect(url_for('admin.tag.index'))

@admin_tag_bp.route('/', methods=['GET'])
@login_required
@admin_required
def index():
    tags = get_all_tags()
    return render_template('admin/tags/index.html', tags=tags)

@admin_tag_bp.route('/<int:id>/edit', methods=['GET', 'POST'])  # Updated from .update to .edit
@login_required
@admin_required
def edit(id):
    tag = get_tag_by_id(id)
    if not tag:
        flash_message(FLASH_MESSAGES["GENERIC_ERROR"], FLASH_CATEGORY_ERROR)
        return redirect(url_for('admin.tag.index'))
    
    form = TagForm(obj=tag, original_name=tag.name)
    
    if form.validate_on_submit():
        try:
            update_tag(tag, form.data)
            flash_message(FLASH_MESSAGES["UPDATE_TAG_SUCCESS"], FLASH_CATEGORY_SUCCESS)
            return redirect(url_for('admin.tag.index'))
        except IntegrityError as e:
            db.session.rollback()
            flash_message(FLASH_MESSAGES["UPDATE_TAG_ERROR"], FLASH_CATEGORY_ERROR)
            return render_template('admin/tags/update.html', form=form, tag=tag)
        except Exception as e:
            db.session.rollback()
            flash_message(FLASH_MESSAGES["UPDATE_TAG_ERROR"], FLASH_CATEGORY_ERROR)
            return render_template('admin/tags/update.html', form=form, tag=tag)

    return render_template('admin/tags/update.html', form=form, tag=tag)
