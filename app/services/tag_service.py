from app.models.tag import Tag
from app.services.base_service import BaseService
from sqlalchemy.exc import SQLAlchemyError
from wtforms.validators import ValidationError

class TagService(BaseService):
    def __init__(self):
        super().__init__(Tag)

    def create(self, data):
        """Create a new tag with validation"""
        self._validate_tag_data(data)
        return super().create(data)

    def update(self, tag, data):
        """Update tag with validation"""
        self._validate_tag_data(data)
        return super().update(tag, data)

    def _validate_tag_data(self, data):
        """Validate tag data"""
        if not data.get('name'):
            raise ValidationError('Name cannot be empty.')
        if not data.get('category'):
            raise ValidationError('Category cannot be empty.')

# Create service instance for use in controllers
tag_service = TagService()
