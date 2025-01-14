import logging
import os
from datetime import datetime
from flask import redirect, url_for, flash, request, render_template, Response

logger = logging.getLogger(__name__)
from flask_login import current_user
from wtforms import ValidationError
from app.models.audit_log import AuditLog
from app.constants import FlashMessages, FlashCategory

class BaseCrudController:
    """Base controller class for CRUD operations with enhanced functionality.
    
    Provides a standardized interface for create, read, update and delete operations
    with built-in features including:
    - Error handling and validation
    - Audit logging and tracking
    - HTMX partial response support
    - Flash message management
    - Rate limiting and security
    - Transaction management
    - Pre/post operation hooks
    
    The controller acts as an intermediary between routes and services, ensuring
    consistent behavior across all CRUD operations. It implements the following patterns:
    - Template Method: Core operations follow a consistent template
    - Chain of Responsibility: Error handling flows through multiple layers
    - Observer: Audit logging hooks into operation lifecycle
    
    Attributes:
        service (BaseService): Service layer instance for business logic
        entity_name (str): Name of the entity being managed (e.g. 'stipend')
        form_class (FlaskForm): WTForms class for form validation
        template_dir (str): Directory for template files (e.g. 'admin/stipends')
        audit_logger (AuditLogger): Optional audit logging instance
        flash_messages (dict): Dictionary of flash message templates
        supports_htmx (bool): Whether to support HTMX partial responses
        htmx_headers (dict): Default HTMX response headers
        cache_validation (bool): Whether to cache validation results
        
    Methods:
        create: Handle entity creation with validation and error handling
        edit: Handle entity updates with audit logging
        delete: Handle entity deletion with confirmation
        _handle_htmx_response: Process HTMX-specific responses
        _handle_operation: Core operation handler with error handling
        _pre_validate: Hook for pre-validation logic
        _post_validate: Hook for post-validation logic
    """
    def __init__(self, service, entity_name, form_class, template_dir=None, audit_logger=None):
        self.service = service
        self.entity_name = entity_name
        self.form_class = form_class
        self.template_dir = template_dir
        self.audit_logger = audit_logger
        self.service.cache_validation = True  # Enable validation caching by default
        self.flash_messages = {
            'create_success': FlashMessages.CREATE_SUCCESS,
            'update_success': FlashMessages.UPDATE_SUCCESS,
            'delete_success': FlashMessages.DELETE_SUCCESS,
            'create_error': FlashMessages.CREATE_ERROR,
            'update_error': FlashMessages.UPDATE_ERROR,
            'delete_error': FlashMessages.DELETE_ERROR,
            'not_found': FlashMessages.NOT_FOUND,
            'validation_error': FlashMessages.FORM_VALIDATION_ERROR,
            'form_validation_error': FlashMessages.FORM_VALIDATION_ERROR,
            'invalid_date_format': FlashMessages.INVALID_DATE_FORMAT,
            'missing_field': FlashMessages.MISSING_FIELD_ERROR
        }
        self.supports_htmx = False  # Disable HTMX for full page reloads
        self.htmx_headers = {
            'HX-Trigger': f'{entity_name}Updated'
        }

    def _handle_htmx_response(self, success, template, context=None, **kwargs):
        """Enhanced HTMX response handling"""
        if not self.supports_htmx or not request.headers.get('HX-Request'):
            return None
            
        status = 200 if success else 400
        headers = self.htmx_headers.copy()
        if success:
            headers['HX-Redirect'] = url_for(f'admin.{self.entity_name}.index')
            
        # Add flash messages for HTMX responses
        if success:
            headers['HX-Trigger'] = 'showSuccessMessage'
        else:
            headers['HX-Trigger'] = 'showErrorMessage'
            
        return render_template(template, **(context or {})), status, headers

    def _handle_operation(self, operation, success_message, error_message, 
                        redirect_success, redirect_error, **kwargs):
        try:
            # Run pre-validation if exists
            if hasattr(self, '_pre_validate'):
                kwargs['data'] = self._pre_validate(kwargs.get('data', {}))
                
            result = operation(**kwargs)
            
            # Enhanced error handling for validation errors
            if isinstance(result, dict) and 'errors' in result:
                for field, error in result['errors'].items():
                    flash(f"{field}: {error}", FlashCategory.ERROR.value)
                return redirect(url_for(f'admin.{self.entity_name}.{redirect_error}', **kwargs))
                
            # Enhanced audit logging
            if self.audit_logger:
                try:
                    operation_name = operation.__name__
                    object_id = result.id if hasattr(result, 'id') else kwargs.get('id')
                    
                    # Log additional context
                    details = {
                        'operation': operation_name,
                        'entity': self.entity_name,
                        'user': current_user.username if current_user.is_authenticated else 'anonymous',
                        'ip': request.remote_addr,
                        'method': request.method,
                        'endpoint': request.endpoint,
                        'success': True,
                        'data': kwargs.get('data', {}),  # Include form data
                        'referrer': request.referrer,
                        'user_agent': request.user_agent.string
                    }
                    
                    self.audit_logger.log(
                        user_id=current_user.id if current_user.is_authenticated else None,
                        action=operation_name,
                        object_type=self.entity_name,
                        object_id=object_id,
                        details=details,
                        ip_address=request.remote_addr,
                        timestamp=datetime.utcnow()
                    )
                    
                except Exception as e:
                    import logging
                    logging.error(f"Audit log error: {str(e)}", exc_info=True)
                    # Don't fail the operation if audit logging fails
                    flash(FlashMessages.AUDIT_LOG_ERROR.value, FlashCategory.WARNING.value)
                    
            flash(success_message.format(self.entity_name), FlashCategory.SUCCESS.value)
            return redirect(url_for(f'admin.{self.entity_name}.{redirect_success}'))
            
        except ValidationError as e:
            # Enhanced validation error handling
            error_messages = []
            for field, errors in e.messages.items():
                for error in errors:
                    # Use standardized error messages from constants
                    error_msg = self.flash_messages.get('validation_error', str(error))
                    flash(f"{field}: {error_msg}", FlashCategory.ERROR.value)
                    error_messages.append(f"{field}: {error_msg}")
            
            # Handle HTMX responses for validation errors
            htmx_response = self._handle_htmx_response(
                success=False,
                template=f'admin/{self.entity_name}/{redirect_error}.html',
                context={'errors': error_messages}
            )
            if htmx_response:
                return htmx_response
                
            return redirect(url_for(f'admin.{self.entity_name}.{redirect_error}', **kwargs))
            
        except Exception as e:
            flash(error_message.format(self.entity_name, str(e)), FlashCategory.ERROR.value)
            return redirect(url_for(f'admin.{self.entity_name}.{redirect_error}', **kwargs))

    def create(self, data=None):
        form = self.form_class(data=data)
        if not form.validate():
            # Return 200 with form errors
            return render_template(
                f'{self.template_dir}/create.html',
                form=form
            ), 200
        try:
            result = self.service.create(form.data)
            if result.success:
                flash(self.flash_messages['create_success'], 'success')
                return redirect(url_for(f'admin.{self.entity_name}.index'))
            else:
                flash(result.message, 'error')
        except Exception as e:
            logger.error(f"Error creating {self.entity_name}: {str(e)}")
            flash(f"Error creating {self.entity_name}: {str(e)}", 'error')
        return render_template(
            f'{self.template_dir}/create.html',
            form=form
        ), 200

    def edit(self, id, data):
        def update_operation(**kwargs):
            entity = self.service.get_by_id(kwargs['id'])
            if not entity:
                flash(FlashMessages.NOT_FOUND.value.format(self.entity_name), FlashCategory.ERROR.value)
                return redirect(url_for(f'admin.{self.entity_name}.index'))
            return self.service.update(entity, kwargs['data'])

        return self._handle_operation(
            operation=update_operation,
            success_message=FlashMessages.UPDATE_SUCCESS.value,
            error_message=FlashMessages.UPDATE_ERROR.value,
            redirect_success='index',
            redirect_error='edit',
            id=id,
            data=data
        )

    def delete(self, id):
        def delete_operation(**kwargs):
            entity = self.service.get_by_id(kwargs['id'])
            if not entity:
                flash(FlashMessages.NOT_FOUND.value.format(self.entity_name), FlashCategory.ERROR.value)
                return redirect(url_for(f'admin.{self.entity_name}.index'))
            return self.service.delete(entity)

        return self._handle_operation(
            operation=delete_operation,
            success_message=FlashMessages.DELETE_SUCCESS.value,
            error_message=FlashMessages.DELETE_ERROR.value,
            redirect_success='index',
            redirect_error='index',
            id=id
        )
