from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required  # Import login_required here
from app.constants import FLASH_MESSAGES, FLASH_CATEGORY_SUCCESS, FLASH_CATEGORY_ERROR
from app.forms.admin_forms import TagForm
from app.services.tag_service import get_tag_by_id, delete_tag, get_all_tags, create_tag, update_tag
from app.extensions import db
from sqlalchemy.exc import IntegrityError  # Add this import if not already present

admin_tag_bp = Blueprint('tag', __name__, url_prefix='/tags')

@admin_tag_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = TagForm()
    if form.validate_on_submit():
        try:
            new_tag = create_tag(form.data)
            if new_tag is None:
                flash(FLASH_MESSAGES["CREATE_TAG_ERROR"], FLASH_CATEGORY_ERROR)
                return render_template('admin/tags/create.html', form=form)  # Render the form again with an error message
            flash(FLASH_MESSAGES["CREATE_TAG_SUCCESS"], FLASH_CATEGORY_SUCCESS)
            return redirect(url_for('admin.tag.index'))
        except IntegrityError as e:
            db.session.rollback()
            flash(FLASH_MESSAGES["CREATE_TAG_ERROR"], FLASH_CATEGORY_ERROR)
            return render_template('admin/tags/create.html', form=form)  # Render the form again with an error message
        except Exception as e:
            db.session.rollback()
            flash(FLASH_MESSAGES["CREATE_TAG_ERROR"], FLASH_CATEGORY_ERROR)
            return render_template('admin/tags/create.html', form=form)  # Render the form again with an error message
    return render_template('admin/tags/create.html', form=form)

@admin_tag_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    tag = get_tag_by_id(id)
    if tag:
        try:
            delete_tag(tag)
            flash(FLASH_MESSAGES["DELETE_TAG_SUCCESS"], FLASH_CATEGORY_SUCCESS)
        except Exception as e:
            db.session.rollback()
            flash(FLASH_MESSAGES["DELETE_TAG_ERROR"], FLASH_CATEGORY_ERROR)
    else:
        flash(FLASH_MESSAGES["GENERIC_ERROR"], FLASH_CATEGORY_ERROR)  # Use generic error if tag not found
    return redirect(url_for('admin.tag.index'))

@admin_tag_bp.route('/', methods=['GET'])
@login_required
def index():
    tags = get_all_tags()
    return render_template('admin/tags/index.html', tags=tags)

@admin_tag_bp.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    tag = get_tag_by_id(id)
    if not tag:
        flash(FLASH_MESSAGES["GENERIC_ERROR"], FLASH_CATEGORY_ERROR)  # Use generic error if tag not found
        return redirect(url_for('admin.tag.index'))
    
    form = TagForm(obj=tag, original_name=tag.name)  # Pass the original name to the form
    
    if form.validate_on_submit():
        try:
            update_tag(tag, form.data)
            flash(FLASH_MESSAGES["UPDATE_TAG_SUCCESS"], FLASH_CATEGORY_SUCCESS)
            return redirect(url_for('admin.tag.index'))
        except IntegrityError as e:
            db.session.rollback()
            flash(FLASH_MESSAGES["UPDATE_TAG_ERROR"], FLASH_CATEGORY_ERROR)  # Specific message for IntegrityError
            return render_template('admin/tags/update.html', form=form, tag=tag)  # Render the form again with an error message
        except Exception as e:
            db.session.rollback()
            flash(FLASH_MESSAGES["UPDATE_TAG_ERROR"], FLASH_CATEGORY_ERROR)  # Use the same error message
            return render_template('admin/tags/update.html', form=form, tag=tag)  # Render the form again with an error message

    return render_template('admin/tags/update.html', form=form, tag=tag)
