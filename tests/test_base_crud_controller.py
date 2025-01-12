import os
import uuid
from unittest.mock import patch
from flask import Response, url_for
from app.models.user import User
from app.extensions import db
from tests.base_test_case import BaseTestCase
from app.controllers.base_crud_controller import BaseCrudController
from app.models import Tag
from app.forms.admin_forms import TagForm, UserForm, StipendForm
from app.services.tag_service import tag_service
from app.constants import FlashMessages

class TestBaseCrudController(BaseTestCase):
    def setUp(self):
        super().setUp()
        
        # Clean up any existing test data
        User.query.filter(User.username.like('testuser_%')).delete()
        Tag.query.filter(Tag.name.like('TestTag%')).delete()
        db.session.commit()
        
        # Create unique test user
        self.test_user = User(
            username=f'testuser_{uuid.uuid4().hex[:8]}',
            email=f'test{uuid.uuid4().hex[:8]}@example.com',
            password_hash='testhash'
        )
        db.session.add(self.test_user)
        db.session.commit()
        
        # Create test template directory
        os.makedirs('templates/admin/tag', exist_ok=True)
        with open('templates/admin/tag/create.html', 'w') as f:
            f.write('<html></html>')
            
        self.controller = BaseCrudController(
            service=tag_service,
            entity_name='tag',
            form_class=TagForm,
            template_dir='admin/tag'
        )

    @patch('app.controllers.base_crud_controller.render_template')
    def test_create_success(self, mock_render):
        # Mock render_template to return a Flask Response object
        mock_render.return_value = Response(status=200)
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
        # Mock render_template to return a Flask Response object
        mock_render.return_value = Response(status=200)
        form_data = {'name': '', 'category': 'TestCategory'}  # Invalid data
        with self.client:
            self.login()
            response = self.controller.create(form_data)
            self.assertEqual(response.status_code, 200)
            self.assertIn('This field is required.', response.get_data(as_text=True))

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

    def test_create_template_error(self):
        # Simulate a template rendering error
        with patch('app.controllers.base_crud_controller.render_template') as mock_render:
            mock_render.side_effect = Exception("Template rendering failed")
            with self.client:
                self.login()
                response = self.controller.create()
                self.assertEqual(response.status_code, 302)  # Should redirect
                self.assertIn(FlashMessages.TEMPLATE_ERROR.value, response.get_data(as_text=True))

    def test_create_missing_template(self):
        # Use unique test data
        form_data = {
            'username': f'testuser_{uuid.uuid4().hex[:8]}',
            'password': 'testpass',
            'email': f'test{uuid.uuid4().hex[:8]}@example.com'
        }
        
        with self.client:
            self.login()
            response = self.controller.create(form_data)
            self.assertEqual(response.status_code, 302)
            self.assertIn(FlashMessages.TEMPLATE_NOT_FOUND.value, response.get_data(as_text=True))
            
            # Verify no duplicate was created
            user_count = User.query.filter(User.username == form_data['username']).count()
            self.assertEqual(user_count, 0)

    def test_create_template_error(self):
        # Simulate a template rendering error
        with patch('app.controllers.base_crud_controller.render_template') as mock_render:
            mock_render.side_effect = Exception("Template rendering failed")
            with self.client:
                self.login()
                response = self.controller.create()
                self.assertEqual(response.status_code, 302)  # Should redirect
                self.assertIn(FlashMessages.TEMPLATE_ERROR.value, response.get_data(as_text=True))

    def test_create_invalid_form_data(self):
        # Use unique test data
        form_data = {
            'username': f'testuser_{uuid.uuid4().hex[:8]}',
            'password': 'testpass',
            'email': f'test{uuid.uuid4().hex[:8]}@example.com',
            'name': '',  # Invalid data
            'category': 'TestCategory'
        }
        
        self.login()
        response = self.controller.create(form_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(FlashMessages.NAME_REQUIRED.value, response.get_data(as_text=True))
        
        # Verify no duplicate was created
        user_count = User.query.filter(User.username == form_data['username']).count()
        self.assertEqual(user_count, 0)

    def login(self):
        """Helper method to log in test user"""
        with self.client:
            response = self.client.post(url_for('public.login'), data={
                'username': self.test_user.username,
                'password': 'testpass',
                'csrf_token': self.get_csrf_token()
            })
            self.assertEqual(response.status_code, 302)

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
