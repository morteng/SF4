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
        # Add validation hooks
        self.add_pre_validation_hook(self._pre_validate)
        self.add_post_validation_hook(self._post_validate)

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

    def _pre_validate(self, data):
        """Pre-validation hook"""
        # Ensure required fields are present
        required_fields = ['name', 'application_deadline']
        for field in required_fields:
            if field not in data:
                data[field] = None
        return data

    def _post_validate(self, data, errors):
        """Post-validation hook"""
        # Additional validation logic
        if 'application_deadline' in data and data['application_deadline']:
            try:
                deadline = datetime.strptime(data['application_deadline'], '%Y-%m-%d %H:%M:%S')
                if deadline < datetime.now():
                    errors['application_deadline'] = str(FlashMessages.PAST_DATE)
            except ValueError:
                errors['application_deadline'] = str(FlashMessages.INVALID_DATE_FORMAT)

    def _validate_create_data(self, data):
        """Validate stipend data before creation"""
        logger.debug("Validating stipend creation data")
        
        if not data.get('name'):
            logger.error("Name is required")
            raise ValueError(FlashMessages.REQUIRED_FIELD.format(field='name'))
            
        # Validate organization
        if 'organization_id' not in data or not data['organization_id']:
            logger.error("Organization is required")
            raise ValueError('Organization is required.')
            
        org = db.session.get(Organization, data['organization_id'])
        if not org:
            logger.error(f"Invalid organization ID: {data['organization_id']}")
            raise ValueError('Invalid organization selected')

        # Validate application deadline
        if 'application_deadline' in data and data['application_deadline']:
            try:
                datetime.strptime(data['application_deadline'], '%Y-%m-%d %H:%M:%S')
            except ValueError as e:
                logger.error(f"Invalid date format: {data['application_deadline']}")
                raise ValueError(FlashMessages.INVALID_DATE_FORMAT)

    def _validate_update_data(self, data):
        """Validate stipend data before update"""
        self._validate_create_data(data)
