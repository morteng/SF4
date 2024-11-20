from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from app.services.tag_service import get_tag_by_id, delete_tag

tag_bp = Blueprint('admin_tag', __name__)

@tag_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    tag = get_tag_by_id(id)
    if tag:
        delete_tag(tag)
        flash(f'Tag {tag.name} deleted.', 'success')
    else:
        flash('Tag not found.', 'danger')
    return redirect(url_for('admin_tag.index'))

@tag_bp.route('/')
@login_required
def index():
    # Assuming there's a method to get all tags, let's add it here
    # For now, we'll just render an empty template
    return render_template('admin/tag/index.html')
