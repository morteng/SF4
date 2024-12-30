import unittest
from flask import Flask
from app import create_app, db

class AdminTagTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test client and authenticate"""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def test_create_tag_invalid_characters(self):
        """Test creating a tag with invalid characters"""
        # First get the form page to extract CSRF token
        form_page = self.client.get('/admin/tags/create')
        self.assertEqual(form_page.status_code, 200)
        self.assertIn(b'Create New Tag', form_page.data)  # Verify we're on the right page
        
        # Extract CSRF token from the form
        csrf_token = self.extract_csrf_token(form_page.data)
        
        # Submit form with invalid characters
        response = self.client.post(
            '/admin/tags/create',
            data={
                'name': 'Invalid@Name',
                'category': 'Test Category',
                'csrf_token': csrf_token
            },
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid characters in tag name', response.data)

    def extract_csrf_token(self, html):
        """Helper method to extract CSRF token from HTML"""
        import re
        match = re.search(b'name="csrf_token" value="([^"]+)"', html)
        if match:
            return match.group(1).decode('utf-8')
        return None
