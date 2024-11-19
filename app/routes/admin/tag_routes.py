from flask import Blueprint, redirect, url_for, flash, render_template, request
from flask_login import login_required
from app.models.tag import Tag
from app.services.tag_service import get_tag_by_id, delete_tag
from app.extensions import db  # Import db here

admin_tag_bp = Blueprint('admin_tag', __name__, url_prefix='/tags')

@admin_tag_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    tag = get_tag_by_id(id)
    if tag:
        delete_tag(tag)
        flash('Tag deleted successfully.', 'success')
    else:
        flash('Tag not found.', 'danger')
    return redirect(url_for('admin_tag.index'))

@admin_tag_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    from app.forms.admin_forms import TagForm
    form = TagForm()
    if form.validate_on_submit():
        tag = Tag(
            name=form.name.data,
            category=form.category.data
        )
        db.session.add(tag)
        db.session.commit()
        flash('Tag created successfully.', 'success')
        return redirect(url_for('admin_tag.index'))
    return render_template('admin/tag_form.html', form=form)

@admin_tag_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    tag = get_tag_by_id(id)
    if not tag:
        flash('Tag not found.', 'danger')
        return redirect(url_for('admin_tag.index'))
    
    from app.forms.admin_forms import TagForm
    form = TagForm(obj=tag)
    if form.validate_on_submit():
        tag.name = form.name.data
        tag.category = form.category.data
        db.session.commit()
        flash('Tag updated successfully.', 'success')
        return redirect(url_for('admin_tag.index'))
    return render_template('admin/tag_form.html', form=form)
