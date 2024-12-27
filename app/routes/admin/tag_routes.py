from flask import Blueprint, render_template, redirect, url_for, request, current_app
from flask_login import login_required
from app.constants import FlashMessages, FlashCategory
from app.forms.admin_forms import TagForm
from app.utils import format_error_message
from app.services.tag_service import (
    get_tag_by_id,
    delete_tag,
    get_all_tags,
    create_tag,
    update_tag
)
from app.extensions import db  # Ensure this matches how db is defined or imported
from sqlalchemy.exc import IntegrityError  # Import IntegrityError
from app.utils import admin_required, flash_message

admin_tag_bp = Blueprint('tag', __name__, url_prefix='/tags')

@admin_tag_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    form = TagForm()
    if form.validate_on_submit():
        try:
            new_tag = create_tag(form.data)
            if new_tag is None:
                flash_message(FlashMessages.CREATE_TAG_ERROR, FlashCategory.ERROR)
                return render_template('admin/tags/create.html', form=form)
            flash_message(FlashMessages.CREATE_TAG_SUCCESS, FlashCategory.SUCCESS)
            return redirect(url_for('tag.index'))
        except IntegrityError as e:
            db.session.rollback()
            flash_message(FlashMessages.CREATE_TAG_ERROR, FlashCategory.ERROR)
            return render_template('admin/tags/create.html', form=form)
        except Exception as e:
            db.session.rollback()
            flash_message(FlashMessages.CREATE_TAG_ERROR, FlashCategory.ERROR)
            return render_template('admin/tags/create.html', form=form)
    else:
        error_messages = []
        field_errors = {}
        for field_name, errors in form.errors.items():
            field = getattr(form, field_name)
            field_errors[field_name] = []
            for error in errors:
                msg = format_error_message(field, error)
                error_messages.append(msg)
                field_errors[field_name].append(msg)
                flash_message(msg, FlashCategory.ERROR)

    return render_template('admin/tags/create.html', form=form)

@admin_tag_bp.route('/<int:id>/delete', methods=['POST'])
@limiter.limit("3 per minute")
@login_required
@admin_required
def delete(id):
    """Delete tag with audit logging"""
    tag = get_tag_by_id(id)
    if tag:
        try:
            delete_tag(tag)
            flash_message(FlashMessages.DELETE_TAG_SUCCESS, FlashCategory.SUCCESS)
        except Exception as e:
            db.session.rollback()
            flash_message(FlashMessages.DELETE_TAG_ERROR, FlashCategory.ERROR)
    else:
        flash_message(FlashMessages.GENERIC_ERROR, FlashCategory.ERROR)
    return redirect(url_for('admin.tag.index'))  # Change 'tag.index' to 'admin.tag.index'

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
        flash_message(FlashMessages.GENERIC_ERROR, FlashCategory.ERROR)
        return redirect(url_for('tag.index'))
    
    form = TagForm(obj=tag, original_name=tag.name)
    
    if form.validate_on_submit():
        try:
            update_tag(tag, form.data)
            flash_message(FlashMessages.UPDATE_TAG_SUCCESS, FlashCategory.SUCCESS)
            return redirect(url_for('tag.index'))
        except IntegrityError as e:
            db.session.rollback()
            flash_message(FlashMessages.UPDATE_TAG_ERROR, FlashCategory.ERROR)
            return render_template('admin/tags/update.html', form=form, tag=tag)
        except Exception as e:
            db.session.rollback()
            flash_message(FlashMessages.UPDATE_TAG_ERROR, FlashCategory.ERROR)
            return render_template('admin/tags/update.html', form=form, tag=tag)

    # Add a specific flash message for invalid form data
    if request.method == 'POST':
        flash_message(FlashMessages.GENERIC_ERROR, FlashCategory.ERROR)

    return render_template('admin/tags/update.html', form=form, tag=tag)
