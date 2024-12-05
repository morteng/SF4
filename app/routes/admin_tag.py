from flask import Blueprint, render_template, request, redirect, url_for
from app.forms.admin_forms import TagForm
from app.services.tag_service import create_tag, get_tag_by_id, get_all_tags, update_tag

admin_tag_bp = Blueprint('tag_bp', __name__)

@admin_tag_bp.route('/tags/create', methods=['GET', 'POST'])
def create():
    form = TagForm()
    if form.validate_on_submit():
        tag = create_tag(form.name.data, form.category.data)
        return redirect(url_for('tag_bp.index'))
    return render_template('admin/tag_form.html', form=form)

@admin_tag_bp.route('/tags/delete/<int:id>', methods=['POST'])
def delete(id):
    tag = get_tag_by_id(id)
    if tag:
        # Implement tag deletion logic here
        return redirect(url_for('tag_bp.index'))
    return "Tag not found", 404

@admin_tag_bp.route('/tags/', methods=['GET'])
def index():
    tags = get_all_tags()
    return render_template('admin/tag_dashboard.html', tags=tags)

@admin_tag_bp.route('/tags/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    tag = get_tag_by_id(id)
    if not tag:
        return "Tag not found", 404
    form = TagForm(obj=tag)
    if form.validate_on_submit():
        update_tag(tag, form.data)
        return redirect(url_for('tag_bp.index'))
    return render_template('admin/tag_form.html', form=form)
