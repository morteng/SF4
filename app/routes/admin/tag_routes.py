from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from app.forms.admin_forms import TagForm
from app.services.tag_service import get_tag_by_id, delete_tag, get_all_tags, create_tag, update_tag
from app.extensions import db
from sqlalchemy.exc import IntegrityError  # Add this import

admin_tag_bp = Blueprint('tag', __name__, url_prefix='/tags')

@admin_tag_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = TagForm()
    if form.validate_on_submit():
        try:
            new_tag = create_tag(form.data)
            flash('Tag created successfully.', 'success')
            return redirect(url_for('admin.tag.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Failed to create tag: {str(e)}.', 'danger')
    return render_template('admin/tags/create.html', form=form)

@admin_tag_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    tag = get_tag_by_id(id)
    if tag:
        delete_tag(tag)
        flash(f'Tag {tag.name} deleted.', 'success')
    else:
        flash('Tag not found.', 'danger')
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
        flash('Tag not found.', 'danger')
        return redirect(url_for('admin.tag.index'))
    
    form = TagForm(obj=tag, original_name=tag.name)  # Pass the original name to the form
    
    if form.validate_on_submit():
        try:
            update_tag(tag, form.data)
            flash('Tag updated successfully.', 'success')
            return redirect(url_for('admin.tag.index'))
        except IntegrityError as e:
            db.session.rollback()
            flash(f'Failed to update tag: {str(e)}.', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while updating the tag: {str(e)}.', 'danger')
    
    return render_template('admin/tags/update.html', form=form, tag=tag)
