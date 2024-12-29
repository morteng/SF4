from flask import Blueprint, request, redirect, url_for, render_template
from flask_login import login_required
from sqlalchemy.exc import IntegrityError
from app.controllers.base_route_controller import BaseRouteController
from app.services.tag_service import TagService
from app.forms.admin_forms import TagForm
from app.utils import admin_required, flash_message
from app.models import Tag
from app.constants import FlashMessages, FlashCategory
from app.extensions import db

admin_tag_bp = Blueprint('tag', __name__, url_prefix='/tags')
tag_controller = BaseRouteController(
    TagService(),
    'tag',
    TagForm,
    'admin/tags'
)

@admin_tag_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    return tag_controller.create()

@admin_tag_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    return tag_controller.edit(id)

@admin_tag_bp.route('/<int:id>/delete', methods=['POST'])
@limiter.limit("3 per minute")
@login_required
@admin_required
def delete(id):
    return tag_controller.delete(id)

@admin_tag_bp.route('/', methods=['GET'])
@login_required
@admin_required
def index():
    page = request.args.get('page', 1, type=int)
    tags = tag_service.get_all().paginate(page=page, per_page=10, error_out=False)
    return render_template('admin/tags/index.html', tags=tags)

@admin_tag_bp.route('/paginate', methods=['GET'])
@login_required
@admin_required
def paginate():
    page = request.args.get('page', 1, type=int)
    tags = tag_service.get_all().paginate(page=page, per_page=10, error_out=False)
    return render_template('admin/tags/_tags_table.html', tags=tags)

@admin_tag_bp.route('/<int:id>/edit', methods=['GET', 'POST'])  # Updated from .update to .edit
@login_required
@admin_required
def edit(id):
    tag = tag_service.get_by_id(id)
    if not tag:
        flash_message(FlashMessages.GENERIC_ERROR, FlashCategory.ERROR)
        return redirect(url_for('tag.index'))
    
    form = TagForm(obj=tag, original_name=tag.name)
    
    if form.validate_on_submit():
        try:
            tag_service.update(tag, form.data)
            flash_message(FlashMessages.UPDATE_TAG_SUCCESS, FlashCategory.SUCCESS)
            return redirect(url_for('tag.index'))
        except IntegrityError as e:
            db.session.rollback()
            flash_message(FlashMessages.UPDATE_TAG_ERROR, FlashCategory.ERROR)
            return render_template('admin/tags/update.html', form=form, tag=tag)
        except Exception as e:
            db.session.rollback()
            flash_message(FlashMessages.UPDATE_TAG_ERROR, FlashCategory.ERROR)
            return render_template('admin/tags/update.html', form=form, tag=tag)

    # Add a specific flash message for invalid form data
    if request.method == 'POST':
        flash_message(FlashMessages.GENERIC_ERROR, FlashCategory.ERROR)

    return render_template('admin/tags/update.html', form=form, tag=tag)
