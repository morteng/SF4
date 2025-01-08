import pytest
from flask import url_for
from app.models import Organization
from tests.conftest import extract_csrf_token
from tests.admin.test_stipend_management import BaseAdminTest

class TestOrganizationManagement(BaseAdminTest):
    """Tests for organization management functionality"""
    
    def test_create_organization(self, client, db_session):
        """Test organization creation flow"""
        self.client = client
        self.db = db_session
        
        # Get CSRF token
        csrf_token = self.get_csrf_token('admin.organization.create')
        
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
        
        # Verify audit log
        self.verify_audit_log('create_organization', 'Organization', org.id)
        
        # Verify notification
        self.verify_notification('organization_created', f'Organization {org.name} was created')

    def test_duplicate_organization(self, client, db_session, test_org):
        """Test duplicate organization prevention"""
        self.client = client
        self.db = db_session
        self.test_org = test_org
        
        # Get CSRF token
        csrf_token = self.get_csrf_token('admin.organization.create')
        
        # Submit duplicate name
        response = self.client.post(url_for('admin.organization.create'), data={
            'name': self.test_org.name,  # Duplicate
            'description': 'Test description',
            'homepage_url': 'https://example.com',
            'csrf_token': csrf_token
        })
        
        # Verify validation error
        assert response.status_code == 200
        assert b"Organization with this name already exists" in response.data
