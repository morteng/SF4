import logging
from flask import (
    Blueprint, request, redirect, url_for, 
    render_template, flash
)
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from wtforms import ValidationError
from app.extensions import limiter, db
from app.controllers.base_crud_controller import BaseCrudController
from app.services.stipend_service import StipendService
from app.forms.admin_forms import StipendForm
from app.utils import admin_required
from app.models import Stipend, Organization, Tag
from app.constants import FlashMessages

logger = logging.getLogger(__name__)

def get_stipend_by_id(id):
    """Retrieve a stipend by its ID with error handling.
    
    Args:
        id (int): The ID of the stipend to retrieve
        
    Returns:
        Stipend: The retrieved stipend instance
        
    Raises:
        404: If no stipend exists with the given ID
        Exception: If database query fails
        
    Note:
        Uses SQLAlchemy's get_or_404() to automatically handle missing records
    """
    return Stipend.query.get_or_404(id)

def update_stipend(stipend, data, session=None):
    """Update a stipend record with new data and transaction management.
    
    Args:
        stipend (Stipend): The stipend instance to update
        data (dict): Dictionary of new field values
        session (Session): Optional database session to use
        
    Returns:
        Stipend: The updated stipend instance
        
    Raises:
        ValueError: If invalid data is provided
        IntegrityError: If database constraints are violated
        Exception: For other database errors
        
    Note:
        Automatically handles transaction rollback on failure
    """
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
    """Delete a stipend by its ID.
    
    Args:
        id: The ID of the stipend to delete
        
    Raises:
        404: If no stipend exists with the given ID
        Exception: If the deletion fails
    """
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
    admin_stipend_bp = BaseBlueprint('admin_stipend', __name__, url_prefix='/stipends')
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
        data = {
            'name': form.name.data,
            'summary': form.summary.data,
            'description': form.description.data,
            'homepage_url': form.homepage_url.data,
            'application_procedure': form.application_procedure.data,
            'eligibility_criteria': form.eligibility_criteria.data,
            'application_deadline': form.application_deadline.data,
            'open_for_applications': form.open_for_applications.data,
            'organization_id': form.organization_id.data,
            'tags': form.tags.data
        }
        return data

    def _prepare_update_data(self, form):
        data = self._prepare_create_data(form)
        data.update({
            'organization_id': form.organization_id.data,
            'tags': form.tags.data,
            'updated_by': current_user.id
        })
        return data

stipend_controller = StipendController()

@admin_stipend_bp.route('/create', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
@login_required
@admin_required
def create():
    """Handle stipend creation requests."""
    logger.debug("Processing stipend creation request")
    
    form = StipendForm(request.form)
    logger.debug("Stipend form initialized successfully")
    
    # Pre-populate organization choices
    from app.models.organization import Organization
    form.organization_id.choices = [(org.id, org.name) for org in Organization.query.all()]
    
    if request.method == 'POST':
        if not form.validate():
            logger.warning(f"Form validation failed: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"{field}: {error}", 'error')
            return render_template('admin/stipends/create.html', form=form)
            
        try:
            # Use the service layer instead of direct database operations
            form_data = stipend_controller._prepare_create_data(form)
            stipend = stipend_controller.service.create(form_data, current_user.id)
            
            flash(FlashMessages.CREATE_SUCCESS.value, 'success')
            return redirect(url_for('admin.admin_stipend.index'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating stipend: {str(e)}")
            flash(FlashMessages.CREATE_ERROR.value, 'error')
            return render_template('admin/stipends/create.html', form=form)
    
    return render_template('admin/stipends/create.html', form=form)

@admin_stipend_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
@login_required
@admin_required
def edit(id):
    """Handle stipend edit requests."""
    logger.debug(f"Processing edit request for stipend {id}")
    
    stipend = Stipend.query.get_or_404(id)
    form = StipendForm(obj=stipend)
    
    # Populate organization and tags
    form.organization_id.data = stipend.organization_id
    form.tags.data = [tag.id for tag in stipend.tags]
    
    if request.method == 'POST' and form.validate():
        try:
            # Use the service layer for update
            form_data = stipend_controller._prepare_update_data(form)
            updated_stipend = stipend_controller.service.update(id, form_data, current_user.id)
            
            flash(FlashMessages.UPDATE_SUCCESS.value, 'success')
            return redirect(url_for('admin.admin_stipend.index'))
        except Exception as e:
            logger.error(f"Error updating stipend {id}: {str(e)}")
            flash(FlashMessages.UPDATE_ERROR.value, 'error')
    
    return render_template('admin/stipends/edit.html', 
                         form=form, 
                         stipend=stipend)


@admin_stipend_bp.route('/<int:id>/delete', methods=['POST'])
@limiter.limit("3 per minute")
@login_required
@admin_required
def delete(id):
    try:
        stipend = Stipend.query.get_or_404(id)
        db.session.delete(stipend)
        db.session.commit()
        flash(FlashMessages.DELETE_SUCCESS.value, 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting stipend {id}: {str(e)}")
        flash(FlashMessages.DELETE_ERROR.value, 'error')
    return redirect(url_for('admin.admin_stipend.index'))


@admin_stipend_bp.route('/', methods=['GET'])
@login_required
@admin_required
def index():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 10
        stipends = Stipend.query.paginate(page=page, per_page=per_page, error_out=False)
        
        if not stipends.items and page > 1:
            # Redirect to last page if page is out of range
            last_page = stipends.pages or 1
            return redirect(url_for('admin.admin_stipend.index', page=last_page))
            
        return render_template('admin/stipends/index.html', 
                            stipends=stipends,
                            current_page=stipends.page,
                            total_pages=stipends.pages)
    except Exception as e:
        logger.error(f"Error loading stipend index: {str(e)}")
        flash('Error loading stipends', 'error')
        return redirect(url_for('admin.dashboard.dashboard'))


@admin_stipend_bp.route('/paginate', methods=['GET'])
@login_required
@admin_required
def paginate():
    page = request.args.get('page', 1, type=int)
    stipends = Stipend.query.paginate(page=page, per_page=10, error_out=False)
    return render_template('admin/stipends/_stipends_table.html', stipends=stipends)
