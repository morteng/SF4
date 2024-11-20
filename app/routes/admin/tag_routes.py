from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from app.services.tag_service import get_tag_by_id, delete_tag, get_all_tags

tag_bp = Blueprint('admin_tag', __name__, url_prefix='/admin/tags')

@tag_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    """Delete a tag by ID."""
    tag = get_tag_by_id(id)
    if tag:
        delete_tag(tag)
        flash(f'Tag {tag.name} deleted.', 'success')
    else:
        flash('Tag not found.', 'danger')
    return redirect(url_for('admin_tag.index'))

@tag_bp.route('/', methods=['GET'])
@login_required
def index():
    """List all tags."""
    tags = get_all_tags()
    return render_template('admin/tag/index.html', tags=tags)
