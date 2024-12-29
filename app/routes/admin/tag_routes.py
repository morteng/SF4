from flask import Blueprint, request, redirect, url_for, render_template
from flask_login import login_required
from sqlalchemy.exc import IntegrityError
from app.controllers.base_route_controller import BaseRouteController
from app.services.tag_service import TagService
from app.forms.admin_forms import TagForm
from app.utils import admin_required, flash_message
from app.models import Tag
from app.constants import FlashMessages, FlashCategory
from app.extensions import db, limiter

admin_tag_bp = Blueprint('tag', __name__, url_prefix='/tags')
tag_controller = BaseRouteController(
    TagService(),
    'tag',
    TagForm,
    'admin/tags'
)

class TagController(BaseRouteController):
    def __init__(self):
        super().__init__(
            service=TagService(),
            entity_name='tag',
            form_class=TagForm,
            template_dir='admin/tags'
        )

tag_controller = TagController()

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
    try:
        tag = tag_controller.service.get_by_id(id)
        if not tag:
            flash_message(FlashMessages.TAG_NOT_FOUND, FlashCategory.ERROR)
            return redirect(url_for('admin.tag.index'))

        tag_controller.service.delete(tag.id, user_id=current_user.id)
        
        flash_message(FlashMessages.TAG_DELETE_SUCCESS, FlashCategory.SUCCESS)
        return redirect(url_for('admin.tag.index'))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting tag: {str(e)}")
        flash_message(f"{FlashMessages.TAG_DELETE_ERROR}: {str(e)}", FlashCategory.ERROR)
        return redirect(url_for('admin.tag.index'))

@admin_tag_bp.route('/', methods=['GET'])
@login_required
@admin_required
def index():
    page = request.args.get('page', 1, type=int)
    tags = tag_controller.service.get_all().paginate(page=page, per_page=10, error_out=False)
    return render_template('admin/tags/index.html', tags=tags)

@admin_tag_bp.route('/paginate', methods=['GET'])
@login_required
@admin_required
def paginate():
    page = request.args.get('page', 1, type=int)
    tags = tag_controller.service.get_all().paginate(page=page, per_page=10, error_out=False)
    return render_template('admin/tags/_tags_table.html', tags=tags)
