from flask import redirect, url_for, flash
from flask_login import current_user
from app.models.audit_log import AuditLog
from app.constants import FlashMessages, FlashCategory

class BaseCrudController:
    def __init__(self, service, entity_name, form_class, audit_logger=None):
        self.service = service
        self.entity_name = entity_name
        self.form_class = form_class
        self.audit_logger = audit_logger
        self.flash_messages = {
            'create_success': FlashMessages.CREATE_SUCCESS,
            'update_success': FlashMessages.UPDATE_SUCCESS,
            'delete_success': FlashMessages.DELETE_SUCCESS,
            'create_error': FlashMessages.CREATE_ERROR,
            'update_error': FlashMessages.UPDATE_ERROR,
            'delete_error': FlashMessages.DELETE_ERROR,
            'not_found': FlashMessages.NOT_FOUND
        }

    def _handle_operation(self, operation, success_message, error_message, 
                        redirect_success, redirect_error, **kwargs):
        try:
            result = operation(**kwargs)
            if self.audit_logger and hasattr(result, 'id'):
                self.audit_logger.log(
                    operation.__name__,
                    self.entity_name,
                    result.id,
                    f"Operation {operation.__name__} on {self.entity_name}",
                    user_id=current_user.id if current_user.is_authenticated else None
                )
            flash(success_message.format(self.entity_name), FlashCategory.SUCCESS.value)
            return redirect(url_for(f'admin.{self.entity_name}.{redirect_success}'))
        except Exception as e:
            import logging
            logging.error(f"Error in {operation.__name__}: {str(e)}", exc_info=True)
            flash(error_message.format(self.entity_name), FlashCategory.ERROR.value)
            return redirect(url_for(f'admin.{self.entity_name}.{redirect_error}', **kwargs))

    def create(self, data):
        return self._handle_operation(
            operation=self.service.create,
            success_message=FlashMessages.CREATE_SUCCESS.value,
            error_message=FlashMessages.CREATE_ERROR.value,
            redirect_success='index',
            redirect_error='create',
            data=data
        )

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
