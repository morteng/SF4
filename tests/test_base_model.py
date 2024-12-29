from tests.base_test_case import BaseTestCase
from app.models import Stipend, Tag, Organization

class TestBaseModel(BaseTestCase):
    def test_to_dict(self):
        stipend = Stipend.query.first()
        data = stipend.to_dict()
        
        # Test basic fields
        self.assertIn('id', data)
        self.assertIn('name', data)
        self.assertIn('summary', data)
        
        # Test relationship fields
        self.assertIn('organization', data)
        self.assertIn('tags', data)
        
        # Test datetime fields
        self.assertIsInstance(data['created_at'], str)
        self.assertIsInstance(data['updated_at'], str)
        
        # Test custom field
        self.assertIn('is_active', data)

    def test_to_dict_exclude(self):
        stipend = Stipend.query.first()
        data = stipend.to_dict(exclude=['summary', 'description'])
        
        self.assertNotIn('summary', data)
        self.assertNotIn('description', data)
        self.assertIn('name', data)
