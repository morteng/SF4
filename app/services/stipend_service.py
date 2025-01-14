import logging
from datetime import datetime
from app.models.stipend import Stipend
from app.models.organization import Organization
from app.models.tag import Tag
from app.services.base_service import BaseService
from app.extensions import db
from app.constants import FlashMessages, FlashCategory

logger = logging.getLogger(__name__)

class StipendService(BaseService):
    """Service layer for stipend-related business logic with enhanced features.
    
    Provides a robust interface for managing stipend data including:
    - CRUD operations with validation
    - Audit logging and tracking
    - Relationship management (organizations, tags)
    - Rate limiting and security
    - Pre/post operation hooks
    
    Inherits from BaseService and adds stipend-specific functionality.
    
    Attributes:
        model (Stipend): The Stipend model class
        audit_logger (AuditLogger): Optional audit logging instance
        limiter (Limiter): Rate limiter instance
        rate_limits (dict): Dictionary of rate limits for operations
        validation_rules (dict): Stipend-specific validation rules
        
    Methods:
        get_form_choices: Get options for form dropdowns
        _pre_validate: Pre-validation hook
        _post_validate: Post-validation hook
        _validate_create_data: Validate data before creation
        _validate_update_data: Validate data before update
        _log_pre_update: Log state before update
        _log_post_update: Log state after update
        _log_pre_delete: Log state before deletion
        _log_post_delete: Log state after deletion
    """
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
        
        # Validate required fields
        required_fields = {
            'name': FlashMessages.REQUIRED_FIELD.format(field='name'),
            'organization_id': 'Organization is required'
        }
        
        for field, error_msg in required_fields.items():
            if not data.get(field):
                logger.error(f"Missing required field: {field}")
                raise ValueError(error_msg)
            
        # Validate organization exists
        org = db.session.get(Organization, data['organization_id'])
        if not org:
            logger.error(f"Invalid organization ID: {data['organization_id']}")
            raise ValueError('Invalid organization selected')

        # Validate application deadline format if present
        if 'application_deadline' in data and data['application_deadline']:
            try:
                datetime.strptime(data['application_deadline'], '%Y-%m-%d %H:%M:%S')
            except ValueError as e:
                logger.error(f"Invalid date format: {data['application_deadline']}")
                raise ValueError(FlashMessages.INVALID_DATE_FORMAT)

    def _validate_update_data(self, data):
        """Validate stipend data before update"""
        self._validate_create_data(data)
