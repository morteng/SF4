from flask import redirect, url_for, render_template, request
from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError
from app.utils import flash_message
from app.constants import FlashMessages, FlashCategory
from app.extensions import db

class BaseRouteController:
    def __init__(self, service, entity_name, form_class, template_dir):
        self.service = service
        self.entity_name = entity_name
        self.form_class = form_class
        self.template_dir = template_dir

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
        form = self.form_class()
        is_htmx = request.headers.get('HX-Request')
        
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
