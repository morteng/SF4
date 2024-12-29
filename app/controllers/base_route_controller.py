from flask import redirect, url_for, flash, render_template, request
from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError
from app.utils import flash_message

class BaseRouteController:
    def __init__(self, service, entity_name, form_class, template_dir):
        self.service = service
        self.entity_name = entity_name
        self.form_class = form_class
        self.template_dir = template_dir

    def create(self):
        form = self.form_class()
        if request.method == 'POST' and form.validate():
            try:
                entity = self.service.create(form.data, current_user.id)
                flash_message(f"{self.entity_name.capitalize()} created successfully", "success")
                return redirect(url_for(f'admin.{self.entity_name}.index'))
            except SQLAlchemyError as e:
                flash_message(f"Error creating {self.entity_name}: {str(e)}", "error")
        return render_template(f'{self.template_dir}/create.html', form=form)

    def edit(self, id):
        entity = self.service.get_by_id(id)
        if not entity:
            flash_message(f"{self.entity_name.capitalize()} not found", "error")
            return redirect(url_for(f'admin.{self.entity_name}.index'))

        form = self.form_class(obj=entity)
        if request.method == 'POST' and form.validate():
            try:
                self.service.update(entity, form.data, current_user.id)
                flash_message(f"{self.entity_name.capitalize()} updated successfully", "success")
                return redirect(url_for(f'admin.{self.entity_name}.index'))
            except SQLAlchemyError as e:
                flash_message(f"Error updating {self.entity_name}: {str(e)}", "error")
        return render_template(f'{self.template_dir}/edit.html', form=form, entity=entity)

    def delete(self, id):
        try:
            self.service.delete(id, current_user.id)
            flash_message(f"{self.entity_name.capitalize()} deleted successfully", "success")
        except SQLAlchemyError as e:
            flash_message(f"Error deleting {self.entity_name}: {str(e)}", "error")
        return redirect(url_for(f'admin.{self.entity_name}.index'))
