import pytest
from app.models.tag import Tag
from app.services.tag_service import tag_service
from app.extensions import db
from app.constants import FlashMessages
from wtforms.validators import ValidationError

class TestTagService(BaseCRUDTest):
    service_class = tag_service.__class__
    model_class = Tag

    @pytest.fixture
    def test_data(self):
        return {
            'name': 'Test Tag',
            'category': 'Test Category'
        }

    def test_create_tag_with_empty_name(self, test_data, db_session, app):
        with app.app_context():
            invalid_data = test_data.copy()
            invalid_data['name'] = ''
            
            with pytest.raises(ValidationError) as exc_info:
                tag_service.create(invalid_data)
            assert FlashMessages.REQUIRED_FIELD.format(field='name') in str(exc_info.value)

    def test_create_tag_with_empty_category(self, test_data, db_session, app):
        with app.app_context():
            invalid_data = test_data.copy()
            invalid_data['category'] = ''
            
            with pytest.raises(ValidationError) as exc_info:
                tag_service.create(invalid_data)
            assert FlashMessages.REQUIRED_FIELD.format(field='category') in str(exc_info.value)

    def test_update_tag_with_empty_name(self, test_data, db_session, app):
        with app.app_context():
            # Create initial tag
            tag = tag_service.create(test_data)
            
            # Try to update with empty name
            invalid_data = test_data.copy()
            invalid_data['name'] = ''
            
            with pytest.raises(ValidationError) as exc_info:
                tag_service.update(tag.id, invalid_data)
            assert FlashMessages.REQUIRED_FIELD.format(field='name') in str(exc_info.value)

    def test_update_tag_with_empty_category(self, test_data, db_session, app):
        with app.app_context():
            # Create initial tag
            tag = tag_service.create(test_data)
            
            # Try to update with empty category
            invalid_data = test_data.copy()
            invalid_data['category'] = ''
            
            with pytest.raises(ValidationError) as exc_info:
                tag_service.update(tag.id, invalid_data)
            assert FlashMessages.REQUIRED_FIELD.format(field='category') in str(exc_info.value)
