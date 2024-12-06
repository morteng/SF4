from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from app.forms.admin_forms import TagForm
from app.services.tag_service import create_tag, get_tag_by_id, get_all_tags, update_tag, delete_tag
from app.extensions import db

admin_tag_bp = Blueprint('admin_tag', __name__, url_prefix='/admin/tags')

@admin_tag_bp.route('/tags/create', methods=['GET', 'POST'])
@login_required
def create():
    form = TagForm()
    if form.validate_on_submit():
        tag = create_tag(form.name.data, form.category.data)
        return redirect(url_for('admin_tag.index'))
    return render_template('admin/tag_form.html', form=form)

@admin_tag_bp.route('/tags/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    tag = get_tag_by_id(id)
    if tag:
        db.session.delete(tag)
        db.session.commit()
        return redirect(url_for('admin_tag.index'))
    return "Tag not found", 404

@admin_tag_bp.route('/tags/', methods=['GET'])
@login_required
def index():
    tags = get_all_tags()
    return render_template('admin/tag_dashboard.html', tags=tags)

@admin_tag_bp.route('/tags/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    tag = get_tag_by_id(id)
    if not tag:
        return "Tag not found", 404
    form = TagForm(obj=tag)
    if form.validate_on_submit():
        update_tag(tag, form.name.data, form.category.data)
        return redirect(url_for('admin_tag.index'))
    return render_template('admin/tag_form.html', form=form)
