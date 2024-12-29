import logging
from flask import (
    Blueprint, request, redirect, url_for, 
    render_template, current_app, render_template_string
)

logger = logging.getLogger(__name__)
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from wtforms import ValidationError
from app.extensions import limiter, db
from app.controllers.base_crud_controller import BaseCrudController
from app.services.stipend_service import StipendService
from app.forms.admin_forms import StipendForm
from app.utils import (
    admin_required, flash_message, 
    log_audit, create_notification,
    format_error_message
)
from app.models import Stipend, Organization, Tag
from app.constants import FlashMessages, FlashCategory

def get_stipend_by_id(id):
    return Stipend.query.get_or_404(id)

def update_stipend(stipend, data, session=None):
    session = session or db.session
    try:
        for key, value in data.items():
            setattr(stipend, key, value)
        session.commit()
        return stipend
    except Exception as e:
        session.rollback()
        raise e

def delete_stipend(id):
    stipend = get_stipend_by_id(id)
    db.session.delete(stipend)
    db.session.commit()

admin_stipend_bp = Blueprint('stipend', __name__, url_prefix='/stipends')

def register_stipend_routes(app):
    """Register stipend routes with the application"""
    app.register_blueprint(admin_stipend_bp)
    app.logger.debug("Registered stipend routes:")
    for rule in app.url_map.iter_rules():
        if rule.endpoint.startswith('admin.stipend'):
            app.logger.debug(f"Route: {rule}")

def register_stipend_routes(app):
    """Register stipend routes with the application"""
    app.register_blueprint(admin_stipend_bp)
    app.logger.debug("Registered stipend routes:")
    for rule in app.url_map.iter_rules():
        if rule.endpoint.startswith('admin.stipend'):
            app.logger.debug(f"Route: {rule}")

class StipendController(BaseCrudController):
    def __init__(self):
        super().__init__(
            service=StipendService(),
            entity_name='stipend',
            form_class=StipendForm,
            template_dir='admin/stipends'
        )
        
    def _prepare_create_data(self, form):
        return {
            'name': form.name.data,
            'summary': form.summary.data,
            'description': form.description.data,
            'homepage_url': form.homepage_url.data,
            'application_procedure': form.application_procedure.data,
            'eligibility_criteria': form.eligibility_criteria.data,
            'application_deadline': form.application_deadline.data,
            'open_for_applications': form.open_for_applications.data
        }

    def _prepare_update_data(self, form):
        data = self._prepare_create_data(form)
        data['organization_id'] = form.organization_id.data
        data['tags'] = form.tags.data
        return data

stipend_controller = StipendController()

@admin_stipend_bp.route('/create', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
@login_required
@admin_required
def create():
    logger.debug("Processing stipend creation request")
    try:
        return stipend_controller.create()
    except Exception as e:
        logger.error(f"Error creating stipend: {str(e)}")
        current_app.logger.error(f"Stipend creation failed: {str(e)}")
        raise

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
    page = request.args.get('page', 1, type=int)
    stipends = Stipend.query.paginate(page=page, per_page=10, error_out=False)
    return render_template('admin/stipends/index.html', 
                         stipends=stipends,
                         current_page=stipends.page,
                         total_pages=stipends.pages)


@admin_stipend_bp.route('/paginate', methods=['GET'])
@login_required
@admin_required
def paginate():
    page = request.args.get('page', 1, type=int)
    stipends = Stipend.query.paginate(page=page, per_page=10, error_out=False)
    return render_template('admin/stipends/_stipends_table.html', stipends=stipends)
