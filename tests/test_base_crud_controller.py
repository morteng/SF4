import os
import uuid
from unittest.mock import patch
from flask import Response, url_for
from app.models.user import User
from app.models.stipend import Stipend
from app.extensions import db
from tests.base_test_case import BaseTestCase
from app.controllers.base_crud_controller import BaseCrudController
from app.models import Tag
from app.forms.admin_forms import TagForm, UserForm, StipendForm
from app.services.tag_service import tag_service
from app.constants import FlashMessages
from app import create_app
from tests.conftest import extract_csrf_token

# Create test app instance
app = create_app('testing')

class TestBaseCrudController(BaseTestCase):
    def setUp(self):
        # Create all database tables
        db.create_all()
        
        # Create unique test user with hashed password
        self.test_user = User(
            username=f'testuser_{uuid.uuid4().hex[:8]}',
            email=f'test{uuid.uuid4().hex[:8]}@example.com',
            is_admin=True
        )
        self.test_user.set_password('testpass')
        db.session.add(self.test_user)
        db.session.commit()
        
        # Verify password was set correctly
        self.assertTrue(self.test_user.check_password('testpass'))
        
        # Initialize client
        self.client = app.test_client()
        
        # Clear any existing session data
        with self.client.session_transaction() as session:
            session.clear()
        
        # Login before each test using the test user
        self.login(self.test_user.username, 'testpass')
        
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
        # Verify we're logged in
        with self.client.session_transaction() as session:
            self.assertIn('_user_id', session)
            self.assertEqual(session['_user_id'], str(self.test_user.id))
        
        # Get CSRF token for the form
        create_page = self.client.get(url_for('admin.stipend.create'))
        csrf_token = extract_csrf_token(create_page.data)
        
        # Submit invalid form data
        response = self.client.post(url_for('admin.stipend.create'), data={
            'name': '',  # Invalid - empty name
            'csrf_token': csrf_token
        }, follow_redirects=True)
        
        # Verify we get a form error
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'This field is required', response.data)
        
        # Verify no stipend was created
        stipend_count = Stipend.query.filter(Stipend.name == '').count()
        self.assertEqual(stipend_count, 0)

    def get_csrf_token(self):
        """Helper method to get a valid CSRF token"""
        # Make a GET request to trigger CSRF token generation
        self.client.get(url_for('public.login'))
        # Get the CSRF token from the session using context manager
        with self.client.session_transaction() as session:
            return session.get('csrf_token')

    def login(self, username='admin', password='password'):
        """Helper method to log in test user"""
        # First get the login page to get CSRF token
        login_page = self.client.get('/login')
        csrf_token = extract_csrf_token(login_page.data)
        
        # Perform login with valid credentials
        response = self.client.post('/login', data={
            'username': username,
            'password': password,
            'csrf_token': csrf_token
        }, follow_redirects=True)
        
        # Debug logging
        print(f"Login response status: {response.status_code}")
        print(f"Response data: {response.data.decode('utf-8')}")
        
        # Verify we got a successful response
        self.assertEqual(response.status_code, 200)
        
        # Verify we're on the dashboard page
        self.assertIn(b'Dashboard', response.data)
        
        # Verify session contains user ID
        with self.client.session_transaction() as session:
            self.assertIn('_user_id', session)
            # Don't check specific user ID since we're using different users

    def test_login_route(self):
        """Test the login route directly"""
        # Get login page
        response = self.client.get(url_for('public.login'))
        self.assertEqual(response.status_code, 200)
        
        # Extract CSRF token
        csrf_token = extract_csrf_token(response.data)
        
        # Submit login form
        response = self.client.post(url_for('public.login'), data={
            'username': self.test_user.username,
            'password': 'testpass',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        
        # Verify successful login
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.data)

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
