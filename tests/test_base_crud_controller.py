from .base_test_case import BaseTestCase
from app.controllers.base_crud_controller import BaseCrudController
from app.models import Tag
from app.forms.admin_forms import TagForm
from app.services.tag_service import create_tag, update_tag

class TestBaseCrudController(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.controller = BaseCrudController(
            service=create_tag,
            entity_name='tag',
            form_class=TagForm
        )

    def test_create_success(self):
        form_data = {'name': 'New Tag'}
        with self.client:
            self.login()
            response = self.controller.create(form_data)
            self.assertEqual(response.status_code, 302)
            
            tag = Tag.query.filter_by(name='New Tag').first()
            self.assertIsNotNone(tag)

    def test_create_validation_error(self):
        form_data = {'name': ''}  # Invalid data
        with self.client:
            self.login()
            response = self.controller.create(form_data)
            self.assertEqual(response.status_code, 200)
            self.assertIn('Name is required', response.get_data(as_text=True))

    def test_edit_success(self):
        tag = Tag.query.first()
        form_data = {'name': 'Updated Tag'}
        with self.client:
            self.login()
            response = self.controller.edit(tag.id, form_data)
            self.assertEqual(response.status_code, 302)
            
            updated_tag = Tag.query.get(tag.id)
            self.assertEqual(updated_tag.name, 'Updated Tag')

    def test_edit_not_found(self):
        with self.client:
            self.login()
            response = self.controller.edit(999, {'name': 'Test'})
            self.assertEqual(response.status_code, 302)
