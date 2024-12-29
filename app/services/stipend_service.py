from datetime import datetime
from app.models.stipend import Stipend
from app.services.base_service import BaseService
from app.extensions import db
from app.constants import FlashMessages, FlashCategory

class StipendService(BaseService):
    def __init__(self):
        super().__init__(Stipend)
        
    def get_form_choices(self):
        organizations = Organization.query.order_by(Organization.name).all()
        tags = Tag.query.order_by(Tag.name).all()
        return {
            'organization_id': [(org.id, org.name) for org in organizations],
            'tags': [(tag.id, tag.name) for tag in tags]
        }

    def create(self, data, user_id=None):
        """Create a new stipend with validation"""
        self._validate_stipend_data(data)
        return super().create(data, user_id)

    def _validate_update_data(self, data):
        """Stipend-specific update validation"""
        if not data.get('name'):
            raise ValueError(FlashMessages.REQUIRED_FIELD.format(field='name'))
        if 'application_deadline' in data and data['application_deadline']:
            try:
                datetime.strptime(data['application_deadline'], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                raise ValueError(FlashMessages.INVALID_DATE_FORMAT)
