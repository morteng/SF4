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

@admin_tag_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    return tag_controller.edit(id)
