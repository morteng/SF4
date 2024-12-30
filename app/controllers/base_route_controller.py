from flask import redirect, url_for, render_template, request, jsonify, flash, session
import logging
from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import Unauthorized
from app.utils import flash_message
from app.constants import FlashMessages, FlashCategory
from app.extensions import db

class AuthenticationError(Unauthorized):
    """Custom authentication error class"""
    pass

logger = logging.getLogger(__name__)

class BaseRouteController:
    def __init__(self, service, entity_name, form_class, template_dir):
        self.service = service
        self.entity_name = entity_name
        self.form_class = form_class
        self.template_dir = template_dir
        self.supports_htmx = True
        self.flash_messages = {
            'create_success': FlashMessages.CREATE_SUCCESS,
            'update_success': FlashMessages.UPDATE_SUCCESS,
            'delete_success': FlashMessages.DELETE_SUCCESS,
            'validation_error': FlashMessages.FORM_VALIDATION_ERROR,
            'not_found': FlashMessages.NOT_FOUND,
            'error': FlashMessages.GENERIC_ERROR
        }

    def _handle_form_choices(self, form):
        """Handle common form choices setup"""
        if hasattr(self.service, 'get_form_choices'):
            choices = self.service.get_form_choices()
            for field, options in choices.items():
                if hasattr(form, field):
                    getattr(form, field).choices = options
                    
    def _handle_form_validation(self, form):
        """Handle common form validation patterns"""
        if hasattr(self.service, 'validate_form_data'):
            return self.service.validate_form_data(form.data)
        return True

    def _handle_htmx_response(self, template, **kwargs):
        """Handle HTMX responses appropriately"""
        if self.supports_htmx and request.headers.get('HX-Request'):
            return render_template(f'{self.template_dir}/partials/{template}', **kwargs)
        return render_template(f'{self.template_dir}/full/{template}', **kwargs)
        
    def _handle_htmx_flash(self, message, category):
        """Handle flash messages for HTMX requests"""
        if request.headers.get('HX-Request'):
            return render_template('_flash_messages.html', message=message, category=category), 200
        flash_message(message, category)
        return None

    def handle_form_errors(self, form):
        """Handle form validation errors consistently"""
        errors = {field: errors[0] for field, errors in form.errors.items()}
        error_message = self.flash_messages['validation_error']
        
        if self.supports_htmx and request.headers.get('HX-Request'):
            return jsonify({
                'success': False,
                'message': error_message,
                'errors': errors
            }), 400
            
        error_messages = [f"{getattr(form, field).label.text}: {error}" 
                         for field, error in errors.items()]
        return render_template(f'{self.template_dir}/create.html', 
                             form=form, 
                             error_messages=error_messages,
                             main_error=error_message)

    def handle_htmx_response(self, template, context=None):
        """Handle HTMX-specific responses"""
        if context is None:
            context = {}
        if self.supports_htmx:
            return render_template(f"{self.template_dir}/{template}.htmx.html", **context)
        return render_template(f"{self.template_dir}/{template}.html", **context)

    def handle_service_error(self, error):
        """Enhanced error handling with HTMX support and detailed messages"""
        logger.error(f"Error in {self.entity_name} controller: {str(error)}")
        
        # Extract error message from exception or use default
        error_message = str(error) if str(error) else self.flash_messages['error']
        
        # Add error details to audit log
        if hasattr(self.service, 'audit_logger'):
            self.service.audit_logger.log(
                action='error',
                object_type=self.entity_name,
                details=f"Error: {error_message}",
                user_id=current_user.id if current_user.is_authenticated else None,
                ip_address=request.remote_addr,
                http_method=request.method,
                endpoint=request.endpoint
            )
        
        # Handle HTMX response
        if request.headers.get('HX-Request'):
            return jsonify({
                'success': False,
                'message': error_message,
                'error_type': error.__class__.__name__ if error else 'UnknownError'
            }), 400
            
        # Add error to flash messages and return to referrer
        flash_message(error_message, FlashCategory.ERROR)
        
        # For authentication errors, stay on current page
        if isinstance(error, (AuthenticationError, PermissionError)):
            return redirect(request.url)
            
        return redirect(request.referrer or url_for('admin.dashboard.dashboard'))

    def handle_authentication_error(self, error):
        """Specialized handler for authentication errors"""
        logger.error(f"Authentication error: {str(error)}")
        error_message = str(error) if str(error) else "Authentication failed"
        
        # Add to audit log
        if hasattr(self.service, 'audit_logger'):
            self.service.audit_logger.log(
                action='auth_error',
                object_type='User',
                details=f"Auth Error: {error_message}",
                user_id=current_user.id if current_user.is_authenticated else None,
                ip_address=request.remote_addr,
                http_method=request.method,
                endpoint=request.endpoint
            )
        
        # Handle HTMX
        if request.headers.get('HX-Request'):
            return jsonify({
                'success': False,
                'message': error_message,
                'error_type': 'AuthenticationError'
            }), 401
            
        flash_message(error_message, FlashCategory.ERROR)
        return redirect(request.url)


    def _handle_redirect(self):
        """Handle redirect after successful operation"""
        if request.headers.get('HX-Request'):
            return '', 204, {'HX-Redirect': url_for(f'admin.{self.entity_name}.index')}
        return redirect(url_for(f'admin.{self.entity_name}.index'))

    def _handle_audit_logging(self, action, entity, user_id=None, before=None, after=None):
        """Handle audit logging for CRUD operations with HTMX support"""
        if hasattr(self.service, 'audit_logger'):
            self.service.audit_logger.log(
                action=action,
                object_type=self.entity_name,
                object_id=entity.id if entity else None,
                user_id=user_id,
                before=before,
                after=after,
                is_htmx=bool(request.headers.get('HX-Request'))
            )

    def _handle_form_validation(self, form):
        """Handle common form validation patterns"""
        if hasattr(self.service, 'validate_form_data'):
            return self.service.validate_form_data(form.data)
        return True

    def _handle_htmx_flash(self, message, category):
        """Handle flash messages for HTMX requests"""
        if request.headers.get('HX-Request'):
            return render_template('_flash_messages.html'), 200
        flash_message(message, category)
        return None

    def index(self):
        """Handle index/list view"""
        page = request.args.get('page', 1, type=int)
        entities = self.service.get_all().paginate(page=page, per_page=10, error_out=False)
        return render_template(f'{self.template_dir}/index.html', 
                             entities=entities,
                             current_page=entities.page,
                             total_pages=entities.pages)

    def create(self):
        """Handle create operation"""
        logger = logging.getLogger(__name__)
        logger.debug("Starting create operation")
        
        form = self.form_class()
        is_htmx = request.headers.get('HX-Request')
        
        # Debug log CSRF token state
        logger.debug(f"CSRF token in form: {form.csrf_token._value()}")
        logger.debug(f"Session CSRF token: {session.get('csrf_token')}")
        logger.debug(f"Request headers: {dict(request.headers)}")
        logger.debug(f"Session data: {dict(session)}")
        
        if form.validate_on_submit():
            try:
                entity = self.service.create(form.data, current_user.id)
                flash_message(FlashMessages.CREATE_SUCCESS.format(entity_name=self.entity_name), 
                            FlashCategory.SUCCESS)
                
                if is_htmx:
                    return '', 204, {'HX-Redirect': url_for(f'admin.{self.entity_name}.index')}
                return redirect(url_for(f'admin.{self.entity_name}.index'))
            except Exception as e:
                db.session.rollback()
                flash_message(str(e), FlashCategory.ERROR)
                if is_htmx:
                    return render_template(f'{self.template_dir}/_form.html', form=form), 400
        
        if is_htmx:
            return render_template(f'{self.template_dir}/_form.html', form=form)
        return render_template(f'{self.template_dir}/create.html', form=form)

    def edit(self, id):
        """Handle edit operation"""
        entity = self.service.get_by_id(id)
        if not entity:
            flash_message(FlashMessages.NOT_FOUND.format(entity_name=self.entity_name), 
                        FlashCategory.ERROR)
            return redirect(url_for(f'admin.{self.entity_name}.index'))

        form = self.form_class(obj=entity)
        is_htmx = request.headers.get('HX-Request')

        if form.validate_on_submit():
            try:
                updated_entity = self.service.update(entity.id, form.data, current_user.id)
                flash_message(FlashMessages.UPDATE_SUCCESS.format(entity_name=self.entity_name), 
                            FlashCategory.SUCCESS)
                
                if is_htmx:
                    return render_template(f'{self.template_dir}/_row.html', entity=updated_entity), 200, {
                        'HX-Trigger': f'{self.entity_name}Updated'
                    }
                return redirect(url_for(f'admin.{self.entity_name}.index'))
            except Exception as e:
                db.session.rollback()
                flash_message(str(e), FlashCategory.ERROR)
                if is_htmx:
                    return render_template(f'{self.template_dir}/_form.html', form=form, entity=entity), 400
        
        if is_htmx:
            return render_template(f'{self.template_dir}/_form.html', form=form, entity=entity)
        return render_template(f'{self.template_dir}/edit.html', form=form, entity=entity)

    def delete(self, id):
        """Handle delete operation"""
        try:
            self.service.delete(id, current_user.id)
            flash_message(FlashMessages.DELETE_SUCCESS.format(entity_name=self.entity_name), 
                        FlashCategory.SUCCESS)
        except Exception as e:
            db.session.rollback()
            flash_message(str(e), FlashCategory.ERROR)
        
        if request.headers.get('HX-Request'):
            return render_template('_flash_messages.html'), 200
        return redirect(url_for(f'admin.{self.entity_name}.index'))
