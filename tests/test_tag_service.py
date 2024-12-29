from tests.base_test_case import BaseTestCase
from app.services.tag_service import TagService
from wtforms.validators import ValidationError

class TestTagService(BaseTestCase):
    
    def setUp(self):
        super().setUp()
        self.service = TagService()

    def test_create_tag(self):
        valid_data = {
            'name': 'Test Tag',
            'category': 'Test Category'
        }
        invalid_data = {
            'name': '',
            'category': ''
        }
        
        self.assertServiceOperation(self.service, 'create', valid_data, invalid_data)

    def test_update_tag(self):
        tag = self.service.create({
            'name': 'Original Name',
            'category': 'Original Category'
        })
        
        valid_data = {
            'name': 'Updated Name',
            'category': 'Updated Category'
        }
        invalid_data = {
            'name': '',
            'category': ''
        }
        
        self.assertServiceOperation(self.service, 'update', (tag, valid_data), (tag, invalid_data))

    def test_delete_tag(self):
        tag = self.service.create({
            'name': 'Test Tag',
            'category': 'Test Category'
        })
        
        self.service.delete(tag)
        self.assertIsNone(self.service.get_by_id(tag.id))
