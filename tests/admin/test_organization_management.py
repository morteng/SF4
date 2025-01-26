import pytest
from flask import url_for
from app.models import Organization
from tests.utils import extract_csrf_token
from tests.base_test_case import BaseTestCase

class TestOrganizationManagement(BaseTestCase):
    """Tests for organization management functionality"""
    
    def test_create_organization(self):
        """Test organization creation flow"""
        # Get CSRF token through login
        self.client.post('/login', data={
            'username': 'testadmin',
            'password': 'testpassword'
        })
        
        # Get CSRF token from organization create page
        create_page = self.client.get(url_for('admin.organization.create'))
        csrf_token = extract_csrf_token(create_page.data)
        
        # Submit form
        response = self.client.post(url_for('admin.organization.create'), data={
            'name': 'New Organization',
            'description': 'Test description',
            'homepage_url': 'https://example.com',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        
        # Verify response
        assert response.status_code == 200
        assert b"Organization created successfully" in response.data
        
        # Verify database
        org = self.db.query(Organization).filter_by(name='New Organization').first()
        assert org is not None
        assert org.description == 'Test description'

    def test_duplicate_organization(self):
        """Test duplicate organization prevention"""
        # Get CSRF token through login
        self.client.post('/login', data={
            'username': 'testadmin',
            'password': 'testpassword'
        })
        
        # Get CSRF token from organization create page
        create_page = self.client.get(url_for('admin.organization.create'))
        csrf_token = extract_csrf_token(create_page.data)
        
        # Submit duplicate name
        response = self.client.post(url_for('admin.organization.create'), data={
            'name': self.org.name,  # Duplicate
            'description': 'Test description',
            'homepage_url': 'https://example.com',
            'csrf_token': csrf_token
        })
        
        # Verify validation error
        assert response.status_code == 200
        assert b"Organization with this name already exists" in response.data
