from datetime import datetime
from app.models.stipend import Stipend
from app.models.organization import Organization
from app.models.tag import Tag
from app.services.base_service import BaseService
from app.extensions import db
from app.constants import FlashMessages, FlashCategory

class StipendService(BaseService):
    def __init__(self):
        super().__init__(Stipend)
        # Add pre/post hooks for audit logging
        self.add_pre_update_hook(self._log_pre_update)
        self.add_post_update_hook(self._log_post_update)
        self.add_pre_delete_hook(self._log_pre_delete)
        self.add_post_delete_hook(self._log_post_delete)

    def _log_pre_update(self, data):
        """Log state before update"""
        entity = self.get_by_id(data.get('id'))
        self._log_audit('pre_update', entity, before=entity.to_dict())
        return data

    def _log_post_update(self, entity):
        """Log state after update"""
        self._log_audit('post_update', entity, after=entity.to_dict())

    def _log_pre_delete(self, data):
        """Log state before deletion"""
        entity = self.get_by_id(data.get('id'))
        self._log_audit('pre_delete', entity, before=entity.to_dict())
        return data

    def _log_post_delete(self, entity):
        """Log state after deletion"""
        self._log_audit('post_delete', entity)
        
    def get_form_choices(self):
        organizations = Organization.query.order_by(Organization.name).all()
        tags = Tag.query.order_by(Tag.name).all()
        return {
            'organization_id': [(org.id, org.name) for org in organizations],
            'tags': [(tag.id, tag.name) for tag in tags]
        }

    def _validate_create_data(self, data):
        """Validate stipend data before creation"""
        if not data.get('name'):
            raise ValueError(FlashMessages.REQUIRED_FIELD.format(field='name'))
        if 'application_deadline' in data and data['application_deadline']:
            try:
                datetime.strptime(data['application_deadline'], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                raise ValueError(FlashMessages.INVALID_DATE_FORMAT)

    def _validate_update_data(self, data):
        """Validate stipend data before update"""
        self._validate_create_data(data)
