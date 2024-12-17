import unittest
from flask import url_for
from app import create_app, db
from app.models.user import User
from app.models.stipend import Stipend

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
        # Log in as admin
        response = self.login('admin', 'password')
        self.assertEqual(response.status_code, 200)

        # Navigate to the stipend creation page
        response = self.client.get(url_for('admin.stipend.create'))
        self.assertEqual(response.status_code, 200)

        # Create a new stipend
        response = self.client.post(url_for('admin.stipend.create'), data={
            'name': 'Test Stipend',
            'summary': 'This is a test stipend.',
            'description': 'Detailed description of the test stipend.',
            'homepage_url': 'http://example.com/stipend',
            'application_procedure': 'Send an email to admin@example.com',
            'eligibility_criteria': 'Must be a student.',
            'application_deadline': '2023-12-31 23:59:59',
            'open_for_applications': True
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        # Check if the stipend was created successfully
        stipend = Stipend.query.filter_by(name='Test Stipend').first()
        self.assertIsNotNone(stipend)
        self.assertEqual(stipend.summary, 'This is a test stipend.')
        self.assertEqual(stipend.description, 'Detailed description of the test stipend.')
        self.assertEqual(stipend.homepage_url, 'http://example.com/stipend')
        self.assertEqual(stipend.application_procedure, 'Send an email to admin@example.com')
        self.assertEqual(stipend.eligibility_criteria, 'Must be a student.')
        self.assertEqual(stipend.open_for_applications, True)

if __name__ == '__main__':
    unittest.main()
