from flask import redirect, url_for, render_template, request, jsonify, flash
from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import Unauthorized
from app.utils import flash_message
from app.constants import FlashMessages, FlashCategory
from app.extensions import db

class AuthenticationError(Unauthorized):
    """Custom authentication error class"""
    pass

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

    def _prepare_create_data(self, form_data, user_id=None):
        data = form_data.to_dict()
        if user_id:
            data['created_by'] = user_id
        return data

    def _prepare_update_data(self, form_data, user_id=None):
        data = form_data.to_dict()
        if user_id:
            data['updated_by'] = user_id
        return data

    def _handle_create(self, form, user_id=None):
        try:
            data = self._prepare_create_data(form, user_id)
            entity = self.service.create(data, user_id=user_id)
            return entity
        except Exception as e:
            db.session.rollback()
            raise e

    def _handle_update(self, form, entity_id, user_id=None):
        try:
            data = self._prepare_update_data(form, user_id)
            entity = self.service.update(entity_id, data, user_id=user_id)
            return entity
        except Exception as e:
            db.session.rollback()
            raise e

    def _get_template(self, template_name):
        return f"{self.template_dir}/{template_name}"

    def _redirect_after_create(self):
        return redirect(url_for(f"{self.template_dir}.index"))

    def _redirect_after_update(self, entity_id):
        return redirect(url_for(f"{self.template_dir}.edit", id=entity_id))

    def create(self):
        form = self.form_class()
        if form.validate_on_submit():
            entity = self._handle_create(form, current_user.id)
            flash_message(self.flash_messages['create_success'], FlashCategory.SUCCESS)
            return self._redirect_after_create()
        return render_template(self._get_template('create.html'), form=form)

    def edit(self, id):
        entity = self.service.get_by_id(id)
        if not entity:
            flash_message(self.flash_messages['not_found'], FlashCategory.ERROR)
            return self._redirect_after_create()
        form = self.form_class(obj=entity)
        if form.validate_on_submit():
            entity = self._handle_update(form, id, current_user.id)
            flash_message(self.flash_messages['update_success'], FlashCategory.SUCCESS)
            return self._redirect_after_update(id)
        return render_template(self._get_template('edit.html'), form=form, entity=entity)

    def delete(self, id):
        try:
            self.service.delete(id, current_user.id)
            flash_message(self.flash_messages['delete_success'], FlashCategory.SUCCESS)
        except Exception as e:
            db.session.rollback()
            flash_message(str(e), FlashCategory.ERROR)
        return redirect(url_for(f"{self.template_dir}.index"))

    def index(self):
        try:
            page = request.args.get('page', 1, type=int)
            entities = self.service.get_all().paginate(page=page, per_page=10, error_out=False)
            return render_template(self._get_template('index.html'), 
                                 entities=entities,
                                 current_page=entities.page,
                                 total_pages=entities.pages)
        except Exception as e:
            flash_message(str(e), FlashCategory.ERROR)
            return redirect(url_for('admin.dashboard.dashboard'))
