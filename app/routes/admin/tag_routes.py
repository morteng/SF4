from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models.tag import Tag
from app.forms.admin_forms import TagForm
from app.services.tag_service import get_tag_by_id, delete_tag

admin_tag_bp = Blueprint('admin_tag', __name__, url_prefix='/admin/tags')

@admin_tag_bp.route('/')
@login_required
def index():
    from app import db  # Import db within the function to avoid circular imports
    tags = Tag.query.all()
    return render_template('admin/tag_index.html', tags=tags)

@admin_tag_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = TagForm()
    if form.validate_on_submit():
        tag = Tag(
            name=form.name.data,
            category=form.category.data
        )
        from app import db  # Import db within the function to avoid circular imports
        db.session.add(tag)
        db.session.commit()
        flash('Tag created successfully!', 'success')
        return redirect(url_for('admin_tag.index'))
    return render_template('admin/tag_form.html', form=form, title='Create Tag')

@admin_tag_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    tag = get_tag_by_id(id)
    if not tag:
        flash('Tag not found!', 'danger')
        return redirect(url_for('admin_tag.index'))
    
    form = TagForm(obj=tag)
    if form.validate_on_submit():
        tag.name = form.name.data
        tag.category = form.category.data
        from app import db  # Import db within the function to avoid circular imports
        db.session.commit()
        flash('Tag updated successfully!', 'success')
        return redirect(url_for('admin_tag.index'))
    return render_template('admin/tag_form.html', form=form, title='Edit Tag')

@admin_tag_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    tag = get_tag_by_id(id)
    if not tag:
        flash('Tag not found!', 'danger')
        return redirect(url_for('admin_tag.index'))
    
    try:
        delete_tag(tag)
        from app import db  # Import db within the function to avoid circular imports
        db.session.commit()
        flash('Tag deleted successfully!', 'success')
    except Exception as e:
        flash(f'Failed to delete tag: {str(e)}', 'danger')
    
    return redirect(url_for('admin_tag.index'))
