from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.services.tag_service import get_tag_by_id, update_tag, list_all_tags

tag_bp = Blueprint('admin_tag', __name__)

@tag_bp.route('/tags', methods=['GET'])
@login_required
def list_tags():
    from app.services.tag_service import list_all_tags
    tags = list_all_tags()
    return render_template('admin/tag_list.html', tags=tags)

@tag_bp.route('/tags/<int:tag_id>')
@login_required
def tag_details(tag_id):
    tag = get_tag_by_id(tag_id)
    if not tag:
        flash('Tag not found', 'danger')
        return redirect(url_for('admin_tag.list_tags'))
    return render_template('admin/tag_details.html', tag=tag)

@tag_bp.route('/tags/<int:tag_id>/update', methods=['POST'])
@login_required
def update_tag_route(tag_id):
    name = request.form.get('name')
    category = request.form.get('category')
    if update_tag(tag_id, name, category):
        flash('Tag updated successfully', 'success')
    else:
        flash('Failed to update tag', 'danger')
    return redirect(url_for('admin_tag.tag_details', tag_id=tag_id))

# Add other routes as needed
