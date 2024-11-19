# app/routes/admin/tag_routes.py

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from app.models.tag import Tag
from app.forms.admin_forms import TagForm
from app.utils import admin_required
from app import db

admin_tag_bp = Blueprint('admin_tag', __name__, url_prefix='/admin/tags')

@admin_tag_bp.route('/')
@admin_required
def index():
    tags = Tag.query.all()
    return render_template('admin/tags/index.html', tags=tags)

@admin_tag_bp.route('/create', methods=['GET', 'POST'])
@admin_required
def create():
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
    return render_template('admin/tags/create.html', form=form)

@admin_tag_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit(id):
    tag = Tag.query.get_or_404(id)
    form = TagForm(obj=tag)
    if form.validate_on_submit():
        form.populate_obj(tag)
        db.session.commit()
        flash('Tag updated successfully.', 'success')
        return redirect(url_for('admin_tag.index'))
    return render_template('admin/tags/edit.html', form=form, tag=tag)

@admin_tag_bp.route('/delete/<int:id>', methods=['POST'])
@admin_required
def delete(id):
    tag = Tag.query.get_or_404(id)
    db.session.delete(tag)
    db.session.commit()
    flash('Tag deleted successfully.', 'success')
    return redirect(url_for('admin_tag.index'))
