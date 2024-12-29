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
        self.supports_htmx = True
        self.flash_messages = {
            'create_success': FlashMessages.CREATE_SUCCESS,
            'update_success': FlashMessages.UPDATE_SUCCESS,
            'delete_success': FlashMessages.DELETE_SUCCESS,
            'validation_error': FlashMessages.FORM_VALIDATION_ERROR,
            'not_found': FlashMessages.NOT_FOUND
        }

    def _handle_form_choices(self, form):
        """Handle common form choices setup"""
        if hasattr(self.service, 'get_form_choices'):
            choices = self.service.get_form_choices()
            for field, options in choices.items():
                if hasattr(form, field):
                    getattr(form, field).choices = options

    def _handle_htmx_response(self, template, **kwargs):
        """Enhanced HTMX response handling"""
        if self.supports_htmx and request.headers.get('HX-Request'):
            return render_template(f'{self.template_dir}/partials/{template}', **kwargs)
        return render_template(f'{self.template_dir}/full/{template}', **kwargs)

    def _handle_form_errors(self, form):
        """Handle form validation errors consistently"""
        error_messages = []
        for field, errors in form.errors.items():
            for error in errors:
                error_messages.append(f"{getattr(form, field).label.text}: {error}")
        if self.supports_htmx and request.headers.get('HX-Request'):
            return render_template(f'{self.template_dir}/partials/_form.html', 
                                 form=form, error_messages=error_messages), 400
        return render_template(f'{self.template_dir}/create.html', 
                             form=form, error_messages=error_messages)

    def _handle_audit_logging(self, action, entity, user_id=None, before=None, after=None):
        """Enhanced audit logging with HTMX support"""
        if hasattr(self.service, 'audit_logger'):
            details = {
                'action': action,
                'object_type': self.entity_name,
                'object_id': entity.id if entity else None,
                'user_id': user_id,
                'before': before,
                'after': after,
                'is_htmx': bool(request.headers.get('HX-Request'))
            }
            self.service.audit_logger.log(**details)

    def _handle_redirect(self):
        """Handle redirect after successful operation"""
        if request.headers.get('HX-Request'):
            return '', 204, {'HX-Redirect': url_for(f'admin.{self.entity_name}.index')}
        return redirect(url_for(f'admin.{self.entity_name}.index'))

    def _handle_audit_logging(self, action, entity, user_id=None, before=None, after=None):
        """Handle audit logging for CRUD operations"""
        if hasattr(self.service, 'audit_logger'):
            self.service.audit_logger.log(
                action=action,
                object_type=self.entity_name,
                object_id=entity.id if entity else None,
                user_id=user_id,
                before=before,
                after=after
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
