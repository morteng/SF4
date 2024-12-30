from unittest.mock import patch
from tests.base_test_case import BaseTestCase
from app.controllers.base_crud_controller import BaseCrudController
from app.models import Tag
from app.forms.admin_forms import TagForm, UserForm, StipendForm
from app.services.tag_service import tag_service
from app.constants import FlashMessages

class TestBaseCrudController(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.controller = BaseCrudController(
            service=tag_service,
            entity_name='tag',
            form_class=TagForm,
            template_dir='admin/tag'  # Add this line to specify the template directory
        )

    @patch('app.controllers.base_crud_controller.render_template')
    def test_create_success(self, mock_render):
        mock_render.return_value = "Mocked Template"
        form_data = {'name': 'New Tag', 'category': 'TestCategory'}
        with self.client:
            self.login()
            response = self.controller.create(form_data)
            self.assertEqual(response.status_code, 200)
            mock_render.assert_called_once_with(
                'admin/tag/create.html',
                form=self.controller.form_class()
            )
            tag = Tag.query.filter_by(name='New Tag').first()
            self.assertIsNotNone(tag)

    @patch('app.controllers.base_crud_controller.render_template')
    def test_create_validation_error(self, mock_render):
        mock_render.return_value = "Mocked Template"
        form_data = {'name': '', 'category': 'TestCategory'}  # Invalid data
        with self.client:
            self.login()
            response = self.controller.create(form_data)
            self.assertEqual(response.status_code, 200)
            self.assertIn('Name cannot be empty.', response.get_data(as_text=True))

    def test_edit_success(self):
        tag = Tag.query.first()
        form_data = {'name': 'Updated Tag', 'category': 'TestCategory'}
        with self.client:
            self.login()
            response = self.controller.edit(tag.id, form_data)
            self.assertEqual(response.status_code, 302)
            
            updated_tag = Tag.query.get(tag.id)
            self.assertEqual(updated_tag.name, 'Updated Tag')

    def test_edit_not_found(self):
        with self.client:
            self.login()
            response = self.controller.edit(999, {'name': 'Test', 'category': 'TestCategory'})
            self.assertEqual(response.status_code, 302)

    def test_user_form_validation(self):
        # Test valid username
        form = UserForm(username="valid_user123")
        assert form.validate() is True

        # Test missing username
        form = UserForm(username="")
        assert form.validate() is False
        assert FlashMessages.USERNAME_REQUIRED in form.username.errors

        # Test username too short
        form = UserForm(username="ab")
        assert form.validate() is False
        assert FlashMessages.USERNAME_LENGTH in form.username.errors

        # Test invalid characters in username
        form = UserForm(username="invalid@user")
        assert form.validate() is False
        assert FlashMessages.USERNAME_FORMAT in form.username.errors

    def test_stipend_form_validation(self):
        # Test missing name
        form = StipendForm(name="")
        assert form.validate() is False
        assert FlashMessages.NAME_REQUIRED in form.name.errors

        # Test invalid characters in name
        form = StipendForm(name="Invalid@Name")
        assert form.validate() is False
        assert FlashMessages.INVALID_NAME_CHARACTERS in form.name.errors

        # Test name too long
        form = StipendForm(name="a" * 101)
        assert form.validate() is False
        assert FlashMessages.NAME_LENGTH in form.name.errors

        # Test invalid URL
        form = StipendForm(homepage_url="invalid-url")
        assert form.validate() is False
        assert FlashMessages.INVALID_URL in form.homepage_url.errors

        # Test invalid leap year
        form = StipendForm(application_deadline="2023-02-29 12:00:00")
        assert not form.validate()
        assert FlashMessages.INVALID_LEAP_YEAR in form.application_deadline.errors
