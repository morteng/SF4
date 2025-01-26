import pytest
from flask import url_for
from app.models import Stipend, Organization, Tag
from tests.utils import extract_csrf_token

class BaseAdminTest:
    """Base class for admin module tests"""
    
    def get_csrf_token(self, route_name):
        """Helper to get CSRF token for a route"""
        response = self.client.get(url_for(route_name))
        return extract_csrf_token(response.data)
    
    def verify_audit_log(self, action, object_type, object_id):
        """Verify audit log entry was created"""
        from app.models.audit_log import AuditLog
        log = AuditLog.query.filter_by(
            action=action,
            object_type=object_type,
            object_id=object_id
        ).first()
        assert log is not None, f"Audit log for {action} on {object_type} {object_id} not found"
        
    def verify_notification(self, notification_type, message):
        """Verify notification was created"""
        from app.models.notification import Notification
        notification = Notification.query.filter_by(
            type=notification_type,
            message=message
        ).first()
        assert notification is not None, f"Notification {notification_type} with message {message} not found"

class TestStipendManagement(BaseAdminTest):
    """Tests for stipend management functionality"""
    
    def test_create_stipend(self, client, db_session, test_org, test_tag):
        """Test stipend creation flow"""
        self.client = client
        self.db = db_session
        self.test_org = test_org
        self.test_tag = test_tag
        
        # Get CSRF token
        csrf_token = self.get_csrf_token('admin.stipend.create')
        
        # Submit form
        response = self.client.post(url_for('admin.stipend.create'), data={
            'name': 'Test Stipend',
            'summary': 'Test summary',
            'description': 'Test description',
            'homepage_url': 'https://example.com',
            'application_procedure': 'Test procedure',
            'eligibility_criteria': 'Test criteria',
            'organization_id': self.test_org.id,
            'tags': [self.test_tag.id],
            'application_deadline': '2025-12-31 23:59:59',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        
        # Verify response
        assert response.status_code == 200
        assert b"Stipend created successfully" in response.data
        
        # Verify database
        stipend = self.db.query(Stipend).filter_by(name='Test Stipend').first()
        assert stipend is not None
        assert stipend.organization_id == self.test_org.id
        assert self.test_tag in stipend.tags
        
        # Verify audit log
        self.verify_audit_log('create_stipend', 'Stipend', stipend.id)
        
        # Verify notification
        self.verify_notification('stipend_created', f'Stipend {stipend.name} was created')

    def test_stipend_validation(self, client, db_session):
        """Test stipend form validation"""
        self.client = client
        self.db = db_session
        
        # Get CSRF token
        csrf_token = self.get_csrf_token('admin.stipend.create')
        
        # Submit invalid data
        response = self.client.post(url_for('admin.stipend.create'), data={
            'name': '',  # Invalid
            'summary': '',  # Invalid
            'csrf_token': csrf_token
        })
        
        # Verify validation errors
        assert response.status_code == 200
        assert b"This field is required" in response.data
        assert b"Name is required" in response.data
        assert b"Summary is required" in response.data
