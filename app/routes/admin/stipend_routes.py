import logging
from flask import (
    Blueprint, request, redirect, url_for, 
    render_template, current_app, render_template_string, flash
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

def _validate_blueprint_params(name: str, import_name: str) -> None:
    """Validate blueprint creation parameters"""
    if not isinstance(import_name, str) or not import_name:
        raise ValueError("Invalid import name for blueprint")
    if not isinstance(name, str) or not name:
        raise ValueError("Invalid blueprint name")

# Create blueprint with enhanced error handling
try:
    from app.common.utils import BaseBlueprint
    _validate_blueprint_params('admin_stipend', __name__)
    admin_stipend_bp = BaseBlueprint('admin_stipend', __name__, url_prefix='/admin/stipends')
    logger.debug(f"Created stipend blueprint: {admin_stipend_bp.name}")
    logger.debug(f"URL prefix: {admin_stipend_bp.url_prefix}")
    logger.debug(f"Import name: {admin_stipend_bp.import_name}")
except ValueError as e:
    logger.error(f"Blueprint validation error: {str(e)}")
    raise
except Exception as e:
    logger.error(f"Unexpected error creating blueprint: {str(e)}")
    raise

def register_stipend_routes(app) -> None:
    """Register stipend routes with the application
    
    Args:
        app: Flask application instance
        
    Raises:
        ValueError: If app is not a valid Flask application
        RuntimeError: If route registration fails
    """
    if not hasattr(app, 'register_blueprint'):
        raise ValueError("Invalid Flask application instance")
        
    try:
        # Register blueprint with admin prefix
        app.register_blueprint(admin_stipend_bp)
        logger.info("Successfully registered stipend routes")
        
        # Verify routes are registered correctly
        registered_routes = [rule.endpoint for rule in app.url_map.iter_rules()]
        required_routes = [
            'stipend.create',
            'stipend.edit',
            'stipend.delete',
            'stipend.index',
            'stipend.paginate'
        ]
        
        # Check if all required routes are registered
        missing_routes = [route for route in required_routes if route not in registered_routes]
        if missing_routes:
            raise RuntimeError(f"Missing routes: {', '.join(missing_routes)}")
            
        logger.debug("All stipend routes registered successfully")
    except Exception as e:
        logger.error(f"Failed to register stipend routes: {str(e)}")
        raise RuntimeError(f"Route registration failed: {str(e)}")

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
    """Handle stipend creation requests."""
    logger.debug("Processing stipend creation request")
    try:
        form = StipendForm()
        
        if request.method == 'POST':
            if form.validate_on_submit():
                try:
                    form_data = request.form.to_dict()
                    # Process form data
                    stipend = Stipend.create(form_data, current_user.id)
                    db.session.commit()
                    flash(FlashMessages.CREATE_SUCCESS.value, 'success')
                    return redirect(url_for('admin.admin_stipend.index'))
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Database error creating stipend: {str(e)}")
                    flash(FlashMessages.CREATE_ERROR.value, 'error')
                    return render_template('admin/stipends/create.html', form=form)
            else:
                # Handle form validation errors
                for field, errors in form.errors.items():
                    for error in errors:
                        flash(f"{getattr(form, field).label.text}: {error}", 'error')
                return render_template('admin/stipends/create.html', form=form)
        
        return render_template('admin/stipends/create.html', form=form)
        
    except Exception as e:
        logger.error(f"Unexpected error in stipend creation: {str(e)}", exc_info=True)
        flash(FlashMessages.CREATE_ERROR.value, 'error')
        return redirect(url_for('admin.admin_stipend.index'))

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
