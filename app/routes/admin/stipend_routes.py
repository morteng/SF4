from flask import Blueprint, redirect, url_for, render_template, request, jsonify, flash
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from app.controllers.base_crud_controller import BaseCrudController
from app.services.stipend_service import StipendService
from app.forms.stipend_form import StipendForm
from app.utils import admin_required
from app.models import Stipend, Organization, Tag
from app.constants import FlashMessages, FlashCategory
from app.extensions import db, limiter

admin_stipend_bp = Blueprint('admin_stipend', __name__, url_prefix='/stipends')

class StipendController(BaseCrudController):
    def __init__(self):
        super().__init__(
            service=StipendService(),
            entity_name='stipend',
            form_class=StipendForm,
            template_dir='admin.stipends'
        )

    def create(self):
        form = self.form_class()
        form.organization_id.choices = [(org.id, org.name) for org in Organization.query.all()]
        return super().create()

    def edit(self, id):
        entity = self.service.get(id)
        form = self.form_class(obj=entity)
        form.organization_id.choices = [(org.id, org.name) for org in Organization.query.all()]
        return super().edit(id)

stipend_controller = StipendController()

@admin_stipend_bp.route('/create', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
@login_required
@admin_required
def create():
    return stipend_controller.create()

@admin_stipend_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
@login_required
@admin_required
def edit(id):
    return stipend_controller.edit(id)

@admin_stipend_bp.route('/<int:id>/delete', methods=['POST'])
@limiter.limit("3 per minute")
@login_required
@admin_required
def delete(id):
    return stipend_controller.delete(id)

@admin_stipend_bp.route('/', methods=['GET'])
@login_required
@admin_required
def index():
    return stipend_controller.index()

@admin_stipend_bp.route('/paginate', methods=['GET'])
@login_required
@admin_required
def paginate():
    page = request.args.get('page', 1, type=int)
    entities = Stipend.query.paginate(page=page, per_page=10, error_out=False)
    return render_template('admin/stipends/_stipends_table.html', entities=entities)

def register_stipend_routes(app):
    app.register_blueprint(admin_stipend_bp)
