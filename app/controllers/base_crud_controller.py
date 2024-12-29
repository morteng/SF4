from flask import redirect, url_for, flash
from flask_login import current_user
from app.models.audit_log import AuditLog
from app.constants import FlashMessages, FlashCategory

class BaseCrudController:
    def __init__(self, service, entity_name, form_class):
        self.service = service
        self.entity_name = entity_name
        self.form_class = form_class

    def create(self, data):
        try:
            entity = self.service.create(data)
            flash(FlashMessages.CREATE_SUCCESS.value.format(self.entity_name), FlashCategory.SUCCESS.value)
            return redirect(url_for(f'admin.{self.entity_name}.index'))
        except Exception as e:
            flash(FlashMessages.CREATE_ERROR.value.format(self.entity_name), FlashCategory.ERROR.value)
            return redirect(url_for(f'admin.{self.entity_name}.create'))

    def edit(self, id, data):
        try:
            entity = self.service.get_by_id(id)
            if not entity:
                flash(FlashMessages.NOT_FOUND.value.format(self.entity_name), FlashCategory.ERROR.value)
                return redirect(url_for(f'admin.{self.entity_name}.index'))

            updated_entity = self.service.update(entity, data)
            flash(FlashMessages.UPDATE_SUCCESS.value.format(self.entity_name), FlashCategory.SUCCESS.value)
            return redirect(url_for(f'admin.{self.entity_name}.index'))
        except Exception as e:
            flash(FlashMessages.UPDATE_ERROR.value.format(self.entity_name), FlashCategory.ERROR.value)
            return redirect(url_for(f'admin.{self.entity_name}.edit', id=id))

    def delete(self, id):
        try:
            entity = self.service.get_by_id(id)
            if not entity:
                flash(FlashMessages.NOT_FOUND.value.format(self.entity_name), FlashCategory.ERROR.value)
                return redirect(url_for(f'admin.{self.entity_name}.index'))

            self.service.delete(entity)
            flash(FlashMessages.DELETE_SUCCESS.value.format(self.entity_name), FlashCategory.SUCCESS.value)
            return redirect(url_for(f'admin.{self.entity_name}.index'))
        except Exception as e:
            flash(FlashMessages.DELETE_ERROR.value.format(self.entity_name), FlashCategory.ERROR.value)
            return redirect(url_for(f'admin.{self.entity_name}.index'))
