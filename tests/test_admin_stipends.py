import unittest
from unittest.mock import patch
from flask import url_for
from flask.ctx import _cv_app
from app import create_app, db
from app.models.user import User
from app.models.stipend import Stipend
from app.models.organization import Organization
from datetime import datetime  # Import datetime module
from app.constants import FlashMessages

class AdminStipendTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
            # Create admin user with proper permissions
            admin_user = User(
                username='admin', 
                email='admin@example.com',
                is_admin=True
            )
            admin_user.set_password('admin')
            db.session.add(admin_user)
            db.session.commit()

            # Verify admin user creation
            created_user = User.query.filter_by(username='admin').first()
            self.assertIsNotNone(created_user)
            self.assertTrue(created_user.is_admin)
            self.assertTrue(created_user.check_password('admin'))

        # Create an organization
        org = Organization(
            name="Test Org", 
            homepage_url="http://example.com",
            description="Test organization"
        )
        db.session.add(org)
        db.session.commit()
        
        # Create an organization
        org = Organization(
            name="Test Org", 
            homepage_url="http://example.com",
            description="Test organization"
        )
        db.session.add(org)
        db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        
        if hasattr(self, 'app_context'):
            self.app_context.pop()

    def login(self):
        # Get CSRF token from login page
        response = self.client.get(url_for('public.login'))
        self.assertEqual(response.status_code, 200)  # Expect successful login
        
        # Extract CSRF token
        csrf_token = response.data.decode('utf-8').split(
            'name="csrf_token" type="hidden" value="')[1].split('"')[0]
        
        # Log in as admin without follow_redirects to test redirect
        response = self.client.post(url_for('public.login'), data={
            'username': 'admin',
            'password': 'admin',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Verify successful login and admin status
        self.assertIn(b'Login successful', response.data)
        with self.client.session_transaction() as session:
            self.assertIn('_user_id', session)
            self.assertTrue(session.get('is_admin', False))
        
        return response

    def get_csrf_token(self, route_name):
        """Helper method to get CSRF token from a specific route"""
        response = self.client.get(url_for(route_name))
        self.assertEqual(response.status_code, 200)
        try:
            csrf_token = response.data.decode('utf-8').split(
                'name="csrf_token" type="hidden" value="')[1].split('"')[0]
            if not csrf_token:
                raise ValueError("Empty CSRF token")
            return csrf_token
        except (IndexError, ValueError) as e:
            self.fail(f"Failed to extract CSRF token from {route_name}: {str(e)}")

    def create_stipend_with_data(self, form_data):
        """Helper method to create a stipend with form data"""
        # First login to establish session
        self.login()
        
        # Get CSRF token from stipend creation page
        response = self.client.get(url_for('admin.admin_stipend.create'))
        self.assertEqual(response.status_code, 200)
        
        # Extract CSRF token with error handling
        try:
            csrf_token = response.data.decode('utf-8').split(
                'name="csrf_token" type="hidden" value="')[1].split('"')[0]
            if not csrf_token:
                raise ValueError("Empty CSRF token")
        except (IndexError, ValueError) as e:
            self.fail(f"Failed to extract CSRF token: {str(e)}")
        
        # Add CSRF token to form data
        form_data['csrf_token'] = csrf_token
        
        # Submit the form with debug logging
        self.app.logger.debug(f"Submitting form with CSRF token: {csrf_token}")
        self.app.logger.debug(f"Form data: {form_data}")
        
        response = self.client.post(
            url_for('admin.admin_stipend.create'),
            data=form_data,
            follow_redirects=True
        )
        
        self.app.logger.debug(f"Response status: {response.status_code}")
        self.app.logger.debug(f"Response data: {response.data.decode('utf-8')}")
        
        return response

    def test_create_stipend_valid(self):
        # Test valid stipend creation
        response = self.create_stipend_with_data({
            'name': 'Valid Stipend',
            'summary': 'Valid summary',
            'description': 'Valid description',
            'homepage_url': 'http://valid.com',
            'application_procedure': 'Valid procedure',
            'eligibility_criteria': 'Valid criteria',
            'application_deadline': '2024-12-31 23:59:59',
            'organization_id': 1,
            'open_for_applications': 'y'
        })
        self.assertEqual(response.status_code, 200)
        stipend = Stipend.query.filter_by(name='Valid Stipend').first()
        self.assertIsNotNone(stipend)



        try:
            with self.client:
                # Get CSRF token from login page
                response = self.client.get(url_for('public.login'))
                self.assertEqual(response.status_code, 200)
                self.app.logger.debug("CSRF token page loaded successfully")
    
            # Extract CSRF token
            try:
                csrf_token = response.data.decode('utf-8').split(
                    'name="csrf_token" type="hidden" value="')[1].split('"')[0]
                if not csrf_token:
                    raise ValueError("CSRF token is empty")
            except (IndexError, ValueError) as e:
                self.fail(f"Failed to extract CSRF token: {str(e)}")
    
            # Log in as admin with correct password
            response = self.client.post(url_for('public.login'), data={
                'username': 'admin',
                'password': 'admin',  # Use 'admin' as password
                'csrf_token': csrf_token
            }, follow_redirects=True)
    
            self.assertEqual(response.status_code, 200,
                       "Login failed - check admin credentials and CSRF token")
    
            # Verify session and admin status
            with self.client.session_transaction() as session:
                self.assertIn('_user_id', session)
                self.assertEqual(session['_user_id'], '1')
                self.assertTrue(session.get('is_admin', False),
                          "User does not have admin privileges")

            # Get CSRF token for stipend creation form
            response = self.client.get(url_for('admin.admin_stipend.create'))
            self.assertEqual(response.status_code, 200)
            try:
                csrf_token = response.data.decode('utf-8').split(
                    'name="csrf_token" type="hidden" value="')[1].split('"')[0]
                if not csrf_token:
                    raise ValueError("CSRF token is empty")
            except (IndexError, ValueError) as e:
                self.fail(f"Failed to extract CSRF token: {str(e)}")

            # Create stipend with CSRF token
            form_data = {
                'name': 'Test Stipend',
                'summary': 'This is a test stipend.',
                'description': 'Detailed description of the test stipend.',
                'homepage_url': 'http://example.com/stipend',
                'application_procedure': 'Send an email to admin@example.com',
                'eligibility_criteria': 'Must be a student.',
                'application_deadline': '2023-12-31 23:59:59',
                'organization_id': 1,
                'open_for_applications': 'y',
                'csrf_token': csrf_token
            }

            response = self.client.post(url_for('admin.admin_stipend.create'),
                                  data=form_data,
                                  follow_redirects=True)

            self.assertEqual(response.status_code, 200,
                       "Stipend creation failed - check form validation and CSRF token")

            # Verify stipend creation
            stipend = Stipend.query.filter_by(name='Test Stipend').first()
            self.assertIsNotNone(stipend, "Stipend was not created in database")
            self.assertEqual(stipend.summary, 'This is a test stipend.',
                       "Stipend summary does not match")
            self.assertEqual(stipend.description, 'Detailed description of the test stipend.',
                       "Stipend description does not match")
            self.assertEqual(stipend.homepage_url, 'http://example.com/stipend',
                       "Stipend homepage URL does not match")
            self.assertEqual(stipend.application_procedure, 'Send an email to admin@example.com',
                       "Stipend application procedure does not match")
            self.assertEqual(stipend.eligibility_criteria, 'Must be a student.',
                       "Stipend eligibility criteria does not match")
            self.assertTrue(stipend.open_for_applications,
                      "Stipend should be open for applications")
        except Exception as e:
            self.fail(f"Test failed with exception: {str(e)}")
            
            # Extract CSRF token from hidden form field with error handling
            try:
                csrf_token = response.data.decode('utf-8').split(
                    'name="csrf_token" type="hidden" value="')[1].split('"')[0]
                if not csrf_token:
                    raise ValueError("CSRF token is empty")
            except (IndexError, ValueError) as e:
                self.fail(f"Failed to extract CSRF token: {str(e)}")
            
            # Log in as admin with CSRF token
            response = self.client.post(url_for('public.login'), data={
                'username': 'admin',
                'password': 'password',
                'csrf_token': csrf_token
            }, follow_redirects=True)
            
            self.assertEqual(response.status_code, 200,
                           "Login failed - check admin credentials and CSRF token")
            
            # Get CSRF token for stipend creation form
            response = self.client.get(url_for('admin.admin_stipend.create'))
            self.assertEqual(response.status_code, 200)
            try:
                csrf_token = response.data.decode('utf-8').split(
                    'name="csrf_token" type="hidden" value="')[1].split('"')[0]
                if not csrf_token:
                    raise ValueError("CSRF token is empty")
            except (IndexError, ValueError) as e:
                self.fail(f"Failed to extract CSRF token: {str(e)}")
            
            # Create stipend with CSRF token
            form_data = {
                'name': 'Test Stipend',
                'summary': 'This is a test stipend.',
                'description': 'Detailed description of the test stipend.',
                'homepage_url': 'http://example.com/stipend',
                'application_procedure': 'Send an email to admin@example.com',
                'eligibility_criteria': 'Must be a student.',
                'application_deadline': '2023-12-31 23:59:59',
                'organization_id': 1,
                'open_for_applications': 'y',
                'csrf_token': csrf_token
            }
            
            response = self.client.post(url_for('admin.admin_stipend.create'), 
                                      data=form_data,
                                      follow_redirects=True)
            
            self.assertEqual(response.status_code, 200,
                           "Stipend creation failed - check form validation and CSRF token")
            
            # Verify stipend creation
            stipend = Stipend.query.filter_by(name='Test Stipend').first()
            self.assertIsNotNone(stipend, "Stipend was not created in database")
            self.assertEqual(stipend.summary, 'This is a test stipend.',
                           "Stipend summary does not match")
            self.assertEqual(stipend.description, 'Detailed description of the test stipend.',
                           "Stipend description does not match")
            self.assertEqual(stipend.homepage_url, 'http://example.com/stipend',
                           "Stipend homepage URL does not match")
            self.assertEqual(stipend.application_procedure, 'Send an email to admin@example.com',
                           "Stipend application procedure does not match")
            self.assertEqual(stipend.eligibility_criteria, 'Must be a student.',
                           "Stipend eligibility criteria does not match")
            self.assertTrue(stipend.open_for_applications,
                          "Stipend should be open for applications")

    def test_update_stipend(self):
        # Log in as admin
        response = self.login()
        self.assertEqual(response.status_code, 200)

        # Create a new stipend
        stipend = Stipend(
            name='Test Stipend',
            summary='This is a test stipend.',
            description='Detailed description of the test stipend.',
            homepage_url='http://example.com/stipend',
            application_procedure='Send an email to admin@example.com',
            eligibility_criteria='Must be a student.',
            application_deadline=datetime(2023, 12, 31, 23, 59, 59),  # Convert string to datetime
            open_for_applications=True
        )
        db.session.add(stipend)
        db.session.commit()
        
        # Navigate to the stipend update page
        response = self.client.get(url_for('admin.stipend.edit', id=stipend.id))
        self.assertEqual(response.status_code, 200)

        # Update the stipend without including 'open_for_applications' to simulate unchecking
        response = self.client.post(url_for('admin.stipend.edit', id=stipend.id), data={
            'name': 'Updated Test Stipend',
            'summary': 'Updated summary.',
            'description': 'Updated description.',
            'homepage_url': 'http://example.com/updated-stipend',
            'application_procedure': 'Send an email to updated@example.com',
            'eligibility_criteria': 'Must be a student or recent graduate.',
            'application_deadline': datetime(2024, 12, 31, 23, 59, 59).strftime('%Y-%m-%d %H:%M:%S'),
            # 'open_for_applications': 'n'  # Remove this line
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        # Check if the stipend was updated successfully
        stipend = Stipend.query.filter_by(name='Updated Test Stipend').first()
        self.assertIsNotNone(stipend)
        self.assertEqual(stipend.summary, 'Updated summary.')
        self.assertEqual(stipend.description, 'Updated description.')
        self.assertEqual(stipend.homepage_url, 'http://example.com/updated-stipend')
        self.assertEqual(stipend.application_procedure, 'Send an email to updated@example.com')
        self.assertEqual(stipend.eligibility_criteria, 'Must be a student or recent graduate.')
        self.assertFalse(stipend.open_for_applications)  # This should now pass

    def test_delete_stipend(self):
        # Log in as admin
        response = self.login()
        self.assertEqual(response.status_code, 200)

        # Create a new stipend
        stipend = Stipend(
            name='Test Stipend',
            summary='This is a test stipend.',
            description='Detailed description of the test stipend.',
            homepage_url='http://example.com/stipend',
            application_procedure='Send an email to admin@example.com',
            eligibility_criteria='Must be a student.',
            application_deadline=datetime(2023, 12, 31, 23, 59, 59),  # Convert string to datetime
            open_for_applications=True
        )
        db.session.add(stipend)
        db.session.commit()

        # Delete the stipend
        response = self.client.post(url_for('admin.stipend.delete', id=stipend.id), follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Check if the stipend was deleted successfully
        stipend = Stipend.query.filter_by(name='Test Stipend').first()
        self.assertIsNone(stipend)

    def test_stipend_index(self):
        # Log in as admin
        response = self.login()
        self.assertEqual(response.status_code, 200)

        # Create a new stipend
        stipend1 = Stipend(
            name='Test Stipend 1',
            summary='This is test stipend 1.',
            description='Detailed description of test stipend 1.',
            homepage_url='http://example.com/stipend1',
            application_procedure='Send an email to admin@example.com',
            eligibility_criteria='Must be a student.',
            application_deadline=datetime(2023, 12, 31, 23, 59, 59),  # Convert string to datetime
            open_for_applications=True
        )
        stipend2 = Stipend(
            name='Test Stipend 2',
            summary='This is test stipend 2.',
            description='Detailed description of test stipend 2.',
            homepage_url='http://example.com/stipend2',
            application_procedure='Send an email to admin@example.com',
            eligibility_criteria='Must be a student.',
            application_deadline=datetime(2023, 12, 31, 23, 59, 59),  # Convert string to datetime
            open_for_applications=True
        )
        db.session.add(stipend1)
        db.session.add(stipend2)
        db.session.commit()
        
        # Navigate to the stipend index page
        response = self.client.get(url_for('admin.stipend.paginate', page=1))
        self.assertEqual(response.status_code, 200)

        # Check if both stipends are displayed on the index page
        self.assertIn(b'Test Stipend 1', response.data)
        self.assertIn(b'Test Stipend 2', response.data)

    def test_stipend_validation_errors(self):
        # Log in as admin
        response = self.login()
        self.assertEqual(response.status_code, 200)

        # Navigate to the stipend creation page
        response = self.client.get(url_for('admin_stipend.create'))
        self.assertEqual(response.status_code, 200)

        # Create a new stipend with invalid data
        response = self.client.post(url_for('admin_stipend.create'), data={
            'name': '',  # Empty name should trigger validation error
            'summary': 'This is a test stipend.',
            'description': 'Detailed description of the test stipend.',
            'homepage_url': 'invalid-url',  # Invalid URL should trigger validation error
            'application_procedure': 'Send an email to admin@example.com',
            'eligibility_criteria': 'Must be a student.',
            'application_deadline': datetime(2023, 12, 31, 23, 59, 59).strftime('%Y-%m-%d %H:%M:%S'),  # Convert to string
            'open_for_applications': 'y'  # Use 'y' or 'n' for boolean fields in form data
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        # Check if validation errors are displayed
        self.assertIn(b'This field is required.', response.data)
        self.assertIn(b'Invalid URL.', response.data)  # Ensure this matches the expected error message

    def test_create_stipend_with_invalid_organization(self):
        # Log in as admin
        response = self.login()
        self.assertEqual(response.status_code, 200)

        # Attempt to create a stipend with an invalid organization ID
        response = self.client.post(url_for('admin_stipend.create'), data={
            'name': 'Test Stipend',
            'summary': 'This is a test stipend.',
            'description': 'Detailed description of the test stipend.',
            'homepage_url': 'http://example.com/stipend',
            'application_procedure': 'Send an email to admin@example.com',
            'eligibility_criteria': 'Must be a student.',
            'application_deadline': datetime(2023, 12, 31, 23, 59, 59).strftime('%Y-%m-%d %H:%M:%S'),
            'organization_id': 9999,  # Invalid organization ID
            'open_for_applications': 'y'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid organization selected.', response.data)

    def test_create_stipend_with_invalid_open_for_applications(self):
        # Log in as admin
        response = self.login()
        self.assertEqual(response.status_code, 200)

        # Attempt to create a stipend with invalid open_for_applications
        response = self.client.post(url_for('stipend.create'), data={
            'name': 'Test Stipend',
            'summary': 'This is a test stipend.',
            'description': 'Detailed description of the test stipend.',
            'homepage_url': 'http://example.com/stipend',
            'application_procedure': 'Send an email to admin@example.com',
            'eligibility_criteria': 'Must be a student.',
            'application_deadline': '2023-12-31 23:59:59',
            'organization_id': 1,
            'open_for_applications': 'invalid'  # Invalid boolean value
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Open for Applications must be a boolean value.', response.data)

    def test_create_stipend_with_invalid_open_for_applications(self):
        # Log in as admin
        response = self.login()
        self.assertEqual(response.status_code, 200)

        # Attempt to create a stipend with invalid open_for_applications
        response = self.client.post(url_for('stipend.create'), data={
            'name': 'Test Stipend',
            'summary': 'This is a test stipend.',
            'description': 'Detailed description of the test stipend.',
            'homepage_url': 'http://example.com/stipend',
            'application_procedure': 'Send an email to admin@example.com',
            'eligibility_criteria': 'Must be a student.',
            'application_deadline': '2023-12-31 23:59:59',
            'organization_id': 1,
            'open_for_applications': 'invalid'  # Invalid boolean value
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Open for Applications must be a boolean value.', response.data)

    def test_create_stipend_with_invalid_open_for_applications(self):
        # Log in as admin
        response = self.login()
        self.assertEqual(response.status_code, 200)

        # Attempt to create a stipend with invalid open_for_applications
        response = self.client.post(url_for('stipend.create'), data={
            'name': 'Test Stipend',
            'summary': 'This is a test stipend.',
            'description': 'Detailed description of the test stipend.',
            'homepage_url': 'http://example.com/stipend',
            'application_procedure': 'Send an email to admin@example.com',
            'eligibility_criteria': 'Must be a student.',
            'application_deadline': '2023-12-31 23:59:59',
            'organization_id': 1,
            'open_for_applications': 'invalid'  # Invalid boolean value
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Open for Applications must be a boolean value.', response.data)

    def test_create_stipend_with_invalid_open_for_applications(self):
        # Log in as admin
        response = self.login()
        self.assertEqual(response.status_code, 200)

        # Attempt to create a stipend with invalid open_for_applications
        response = self.client.post(url_for('stipend.create'), data={
            'name': 'Test Stipend',
            'summary': 'This is a test stipend.',
            'description': 'Detailed description of the test stipend.',
            'homepage_url': 'http://example.com/stipend',
            'application_procedure': 'Send an email to admin@example.com',
            'eligibility_criteria': 'Must be a student.',
            'application_deadline': '2023-12-31 23:59:59',
            'organization_id': 1,
            'open_for_applications': 'invalid'  # Invalid boolean value
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Open for Applications must be a boolean value.', response.data)

    def test_create_stipend_with_invalid_open_for_applications(self):
        # Log in as admin
        response = self.login()
        self.assertEqual(response.status_code, 200)

        # Attempt to create a stipend with invalid open_for_applications
        response = self.client.post(url_for('admin.stipend.create'), data={
            'name': 'Test Stipend',
            'summary': 'This is a test stipend.',
            'description': 'Detailed description of the test stipend.',
            'homepage_url': 'http://example.com/stipend',
            'application_procedure': 'Send an email to admin@example.com',
            'eligibility_criteria': 'Must be a student.',
            'application_deadline': '2023-12-31 23:59:59',
            'organization_id': 1,
            'open_for_applications': 'invalid'  # Invalid boolean value
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Open for Applications must be a boolean value.', response.data)



    def test_unauthorized_access(self):
        # Create a non-admin user
        user = User(username='user', email='user@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()

        # Log in as the non-admin user
        response = self.client.post(url_for('public.login'), data={
            'username': 'user',
            'password': 'password'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        # Verify session does not have admin privileges
        with self.client.session_transaction() as session:
            self.assertFalse(session.get('is_admin', False),
                       "Non-admin user should not have admin privileges")

        # Attempt to access the stipend creation page (should be unauthorized)
        response = self.client.get(url_for('admin_stipend.create'))
        self.assertEqual(response.status_code, 403)  # Assuming you return a 403 Forbidden

        # Attempt to create a stipend (should be unauthorized)
        response = self.client.post(url_for('admin.stipend.create'), data={
            'name': 'Test Stipend',
            'summary': 'This is a test stipend.',
            'description': 'Detailed description of the test stipend.',
            'homepage_url': 'http://example.com/stipend',
            'application_procedure': 'Send an email to admin@example.com',
            'eligibility_criteria': 'Must be a student.',
            'application_deadline': datetime(2023, 12, 31, 23, 59, 59).strftime('%Y-%m-%d %H:%M:%S'),  # Convert to string
            'open_for_applications': 'y'  # Use 'y' or 'n' for boolean fields in form data
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 403)  # Assuming you return a 403 Forbidden



    def test_login(self):
        """Test admin login functionality"""
        # Get CSRF token from login page
        response = self.client.get(url_for('public.login'))
        self.assertEqual(response.status_code, 200)
        
        # Extract CSRF token
        try:
            csrf_token = response.data.decode('utf-8').split(
                'name="csrf_token" type="hidden" value="')[1].split('"')[0]
            if not csrf_token:
                raise ValueError("Empty CSRF token")
        except (IndexError, ValueError) as e:
            self.fail(f"Failed to extract CSRF token: {str(e)}")
        
        # Test successful login
        response = self.client.post(url_for('public.login'), data={
            'username': 'admin',
            'password': 'admin',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login successful', response.data)
        
        # Verify session contains admin user
        with self.client.session_transaction() as session:
            self.assertIn('_user_id', session)
            self.assertTrue(session.get('is_admin', False))
            
    def test_user_is_active(self):
        # Create a new user
        user = User(username='testuser', email='test@example.com')
        user.set_password('password')
        
        # Verify default is_active status
        self.assertTrue(user.is_active, "New user should be active by default")
        
        # Test setting is_active
        user.is_active = False
        self.assertFalse(user.is_active, "User should be inactive after setting is_active to False")
        
        # Test invalid is_active value
        with self.assertRaises(ValueError):
            user.is_active = 'invalid'



    # TODO: Reimplement missing required fields test after fixing CSRF token handling
    # def test_create_stipend_missing_required_fields(self):
    #     # Test missing required fields with proper CSRF token handling

    def test_create_stipend_missing_required_fields(self):
        # Test missing required fields
        required_fields = [
            'name', 'summary', 'description', 'homepage_url',
            'application_procedure', 'eligibility_criteria',
            'application_deadline', 'organization_id'
        ]
        
        # First login to establish session
        self.login()
        
        # Get CSRF token from stipend creation page
        response = self.client.get(url_for('admin.admin_stipend.create'))
        self.assertEqual(response.status_code, 200)
        
        # Extract CSRF token
        try:
            csrf_token = response.data.decode('utf-8').split(
                'name="csrf_token" type="hidden" value="')[1].split('"')[0]
            if not csrf_token:
                raise ValueError("Empty CSRF token")
        except (IndexError, ValueError) as e:
            self.fail(f"Failed to extract CSRF token: {str(e)}")
    
        for field in required_fields:
            with self.subTest(field=field):
                form_data = {
                    'name': 'Test Stipend',
                    'summary': 'Test summary',
                    'description': 'Test description',
                    'homepage_url': 'http://example.com',
                    'application_procedure': 'Test procedure',
                    'eligibility_criteria': 'Test criteria',
                    'application_deadline': '2023-12-31 23:59:59',
                    'organization_id': 1,
                    'open_for_applications': 'y',
                    'csrf_token': csrf_token
                }
                del form_data[field]  # Remove the required field
    
                response = self.client.post(
                    url_for('admin.admin_stipend.create'),
                    data=form_data,
                    follow_redirects=True
                )
                self.assertEqual(response.status_code, 200)
                self.assertIn(b'Invalid CSRF token', response.data)

    def test_blueprint_registration(self):
        """Test that the admin stipend blueprint is registered correctly."""
        with self.app.app_context():
            registered_routes = [rule.endpoint for rule in self.app.url_map.iter_rules()]
            self.assertIn('admin.admin_stipend.create', registered_routes)  # Updated to match registered route

    def test_route_validation(self):
        """Test that required routes are validated."""
        with patch('app.common.utils.validate_blueprint_routes') as mock_validate:
            self.app = create_app('testing')
            mock_validate.assert_called_once_with(
                self.app,
                ['admin.admin_stipend.create', 'admin.dashboard.dashboard']
            )

if __name__ == '__main__':
    unittest.main()
