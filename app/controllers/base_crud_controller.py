from flask import redirect, url_for, flash
from flask_login import current_user
from app.models.audit_log import AuditLog
from app.constants import FlashMessages, FlashCategory

class BaseCrudController:
    def __init__(self, service, entity_name, form_class):
        self.service = service
        self.entity_name = entity_name
        self.form_class = form_class

    def _handle_operation(self, operation, success_message, error_message, 
                        redirect_success, redirect_error, **kwargs):
        try:
            result = operation(**kwargs)
            flash(success_message.format(self.entity_name), FlashCategory.SUCCESS.value)
            return redirect(url_for(f'admin.{self.entity_name}.{redirect_success}'))
        except Exception as e:
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
