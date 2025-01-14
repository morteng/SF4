import os
import uuid
from datetime import datetime
from unittest.mock import patch
from flask import Response, url_for, request
from flask_login import current_user
from app.models.user import User
from app.models.stipend import Stipend
from app.extensions import db
from tests.base_test_case import BaseTestCase
from app.controllers.base_crud_controller import BaseCrudController
from app.models import Tag
from app.forms.admin_forms import TagForm, UserForm, StipendForm
from app.forms.user_forms import LoginForm
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
            is_admin=True,
            is_active=True
        )
        self.test_user.set_password('testpass')
        db.session.add(self.test_user)
        db.session.commit()
        
        # Verify password hash
        print(f"Test user password hash: {self.test_user.password_hash}")
        print(f"Password check: {self.test_user.check_password('testpass')}")
        
        # Manually confirm the user after creation
        self.test_user.confirmed_at = datetime.utcnow()
        db.session.commit()
        
        # Initialize client with session support
        self.client = app.test_client()
        self.client.testing = True
        
        # Clear any existing session data
        with self.client.session_transaction() as session:
            session.clear()
    
        # Login before each test using the test user
        login_response = self.login()
        
        # Verify login was successful
        self.assertEqual(login_response.status_code, 200)
        self.assertEqual(login_response.status_code, 200)
        self.assertIn(b'Dashboard', login_response.data)
        self.assertIn(b'Recent Activity', login_response.data)
        
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



    def test_create_template_error(self):
        # Simulate a template rendering error
        with patch('app.controllers.base_crud_controller.render_template') as mock_render:
            mock_render.side_effect = Exception("Template rendering failed")
            with self.client:
                self.login()
                response = self.controller.create()
                self.assertEqual(response.status_code, 302)  # Should redirect
                self.assertIn(FlashMessages.TEMPLATE_ERROR.value, response.get_data(as_text=True))


    def get_csrf_token(self):
        """Helper method to get a valid CSRF token"""
        # Make a GET request to trigger CSRF token generation
        self.client.get(url_for('public.login'))
        # Get the CSRF token from the session using context manager
        with self.client.session_transaction() as session:
            return session.get('csrf_token')

    def login(self, username=None, password='testpass'):
        """Helper method to log in test user"""
        if username is None:
            username = self.test_user.username
            
        # Get login page
        login_page = self.client.get(url_for('public.login'))
        print(f"Login page status: {login_page.status_code}")
        
        # Extract CSRF
        csrf_token = extract_csrf_token(login_page.data)
        print(f"CSRF token: {csrf_token}")
        
        # Verify test user exists
        user = User.query.filter_by(username=username).first()
        print(f"Test user exists: {user is not None}")
        print(f"Test user active: {user.is_active if user else False}")
        print(f"Test user password hash: {user.password_hash if user else None}")
        
        # Login POST
        response = self.client.post(url_for('public.login'), data={
            'username': username,
            'password': password,
            'csrf_token': csrf_token,
            'submit': 'Login'
        }, follow_redirects=True)
        
        print(f"Login response status: {response.status_code}")
        print(f"Login response path: {response.request.path}")
        print(f"Response data: {response.data[:500]}")  # Print first 500 chars
        
        # Verify session contains correct user ID
        with self.client.session_transaction() as session:
            print(f"Session user ID: {session.get('_user_id')}")
            print(f"Session fresh: {session.get('_fresh')}")
            print(f"Session keys: {list(session.keys())}")
    
        return response

    def test_login_route(self):
        """Test the login route directly"""
        # Test GET request
        response = self.client.get(url_for('public.login'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)
        
        # Extract CSRF token
        csrf_token = extract_csrf_token(response.data)
        
        # Test POST with valid credentials
        response = self.client.post(url_for('public.login'), data={
            'username': self.test_user.username,
            'password': 'testpass',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.data)
        
        # Verify session data
        with self.client.session_transaction() as session:
            self.assertIn('_user_id', session)
            self.assertEqual(session['_user_id'], str(self.test_user.id))
            self.assertIn('is_admin', session)
            self.assertEqual(session['is_admin'], self.test_user.is_admin)
            self.assertIn('_fresh', session)
            
        # Test POST with invalid credentials
        response = self.client.post(url_for('public.login'), data={
            'username': 'invalid',
            'password': 'wrong',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid username or password', response.data)

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
