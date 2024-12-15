from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from app.forms.admin_forms import TagForm
from app.models.tag import Tag
from app.extensions import db  # Import the db object

admin_tag_bp = Blueprint('admin_tag_bp', __name__)

@admin_tag_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = TagForm()
    if form.validate_on_submit():
        tag = Tag(name=form.name.data, description=form.description.data)
        db.session.add(tag)
        db.session.commit()
        flash('Tag created successfully!', 'success')
        return redirect(url_for('admin_tag_bp.index'))
    return render_template('admin/tag/create.html', form=form)

@admin_tag_bp.route('/')
@login_required
def index():
    tags = Tag.query.all()
    return render_template('admin/tag/index.html', tags=tags)
