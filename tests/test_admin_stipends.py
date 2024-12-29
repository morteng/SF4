import unittest
from flask import url_for
from app import create_app, db
from app.models.user import User
from app.models.stipend import Stipend
from app.models.organization import Organization
from datetime import datetime  # Import datetime module

class AdminStipendTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        # Create an admin user
        admin_user = User(username='admin', email='admin@example.com')
        admin_user.set_password('password')
        admin_user.is_admin = True
        db.session.add(admin_user)
        
        # Create an organization
        org = Organization(
            name="Test Org", 
            homepage_url="http://example.com",
            description="Test organization"
        )
        db.session.add(org)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, username, password):
        return self.client.post(url_for('public.login'), data={
            'username': username,
            'password': password
        }, follow_redirects=True)

    def test_create_stipend(self):
        with self.client:
            # Get CSRF token from login page
            response = self.client.get(url_for('public.login'))
            self.assertEqual(response.status_code, 200)
            
            # Extract CSRF token from form
            csrf_token = response.data.decode('utf-8').split(
                'name="csrf_token" value="')[1].split('"')[0]
            
            # Log in as admin with CSRF token
            response = self.client.post(url_for('public.login'), data={
                'username': 'admin',
                'password': 'password',
                'csrf_token': csrf_token
            }, follow_redirects=True)
            
            self.assertEqual(response.status_code, 200,
                           "Login failed - check admin credentials and CSRF token")
            
            # Get CSRF token for stipend creation form
            response = self.client.get(url_for('admin.stipend.create'))
            self.assertEqual(response.status_code, 200)
            csrf_token = response.data.decode('utf-8').split(
                'name="csrf_token" value="')[1].split('"')[0]
            
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
            
            response = self.client.post(url_for('admin.stipend.create'), 
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
        response = self.login('admin', 'password')
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
        response = self.login('admin', 'password')
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
        response = self.login('admin', 'password')
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
        response = self.login('admin', 'password')
        self.assertEqual(response.status_code, 200)

        # Navigate to the stipend creation page
        response = self.client.get(url_for('admin.stipend.create'))
        self.assertEqual(response.status_code, 200)

        # Create a new stipend with invalid data
        response = self.client.post(url_for('admin.stipend.create'), data={
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
        response = self.login('admin', 'password')
        self.assertEqual(response.status_code, 200)

        # Attempt to create a stipend with an invalid organization ID
        response = self.client.post(url_for('admin.stipend.create'), data={
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
        response = self.login('admin', 'password')
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

    def test_create_stipend_with_invalid_open_for_applications(self):
        # Log in as admin
        response = self.login('admin', 'password')
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

    def test_create_stipend_with_invalid_open_for_applications(self):
        # Log in as admin
        response = self.login('admin', 'password')
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

    def test_create_stipend_with_invalid_open_for_applications(self):
        # Log in as admin
        response = self.login('admin', 'password')
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

    def test_create_stipend_with_invalid_open_for_applications(self):
        # Log in as admin
        response = self.login('admin', 'password')
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

        # Attempt to access the stipend creation page (should be unauthorized)
        response = self.client.get(url_for('admin.stipend.create'))
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

if __name__ == '__main__':
    unittest.main()
