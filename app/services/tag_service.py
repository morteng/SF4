from app.models.tag import Tag
from app.services.base_service import BaseService
from app.constants import FlashMessages
from wtforms.validators import ValidationError

class TagService(BaseService):
    def __init__(self):
        super().__init__(Tag)
        
    def get_form_choices(self):
        return {
            'category': [('general', 'General'), ('specific', 'Specific')]
        }

    def _validate_create_data(self, data):
        """Validate tag data before creation"""
        self._validate_tag_data(data)

    def _validate_update_data(self, data):
        """Validate tag data before update"""
        self._validate_tag_data(data)

    def _validate_tag_data(self, data):
        """Common tag data validation"""
        if not data.get('name'):
            raise ValidationError(FlashMessages.REQUIRED_FIELD.format(field='name'))
        if not data.get('category'):
            raise ValidationError(FlashMessages.REQUIRED_FIELD.format(field='category'))

# Create service instance for use in controllers
tag_service = TagService()
