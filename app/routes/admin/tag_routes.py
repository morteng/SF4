from flask import Blueprint, redirect, url_for, render_template, request
from flask_login import login_required
from app.controllers.base_route_controller import BaseRouteController
from app.services.tag_service import TagService
from app.forms.admin_forms import TagForm
from app.utils import admin_required
from app.models import Tag
from app.constants import FlashMessages, FlashCategory
from app.extensions import db, limiter

admin_tag_bp = Blueprint('admin_tag', __name__, url_prefix='/tags')

class TagController(BaseRouteController):
    def __init__(self):
        super().__init__(
            service=TagService(),
            entity_name='tag',
            form_class=TagForm,
            template_dir='admin.tags'
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
    return tag_controller.delete(id)

@admin_tag_bp.route('/', methods=['GET'])
@login_required
@admin_required
def index():
    return tag_controller.index()
