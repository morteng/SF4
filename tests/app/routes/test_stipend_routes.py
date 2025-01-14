import pytest
from flask import url_for, get_flashed_messages
from app.models import Stipend, Organization
from app.extensions import db
from datetime import datetime
from flask_login import login_user
from app.constants import FlashMessages

def test_create_stipend_route(client, admin_user, test_data):
    """Test stipend creation through route handler"""
    # Create required organization
    org = Organization(name="Test Org")
    db.session.add(org)
    db.session.commit()
    test_data['organization_id'] = org.id

    with client:
        # Login admin user
        login_user(admin_user)
        
        # Test GET request
        response = client.get(url_for('admin.admin_stipend.create'))
        assert response.status_code == 200
        assert b"Create Stipend" in response.data
        
        # Test POST with valid data
        response = client.post(
            url_for('admin.admin_stipend.create'),
            data=test_data,
            follow_redirects=True
        )
        assert response.status_code == 200
        assert FlashMessages.CREATE_SUCCESS.value.encode() in response.data
        
        # Verify stipend was created
        stipend = Stipend.query.filter_by(name=test_data['name']).first()
        assert stipend is not None

def test_create_stipend_invalid_data(client, admin_user):
    """Test stipend creation with invalid data"""
    invalid_data = {
        'name': '',  # Invalid name
        'application_deadline': 'invalid-date'
    }
    
    with client:
        login_user(admin_user)
        response = client.post(
            url_for('admin.admin_stipend.create'),
            data=invalid_data,
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b"Name: This field is required" in response.data
        assert b"Invalid date format" in response.data

def test_edit_stipend_route(client, admin_user, test_data):
    """Test stipend editing through route handler"""
    # Create initial stipend
    stipend = Stipend(**test_data)
    db.session.add(stipend)
    db.session.commit()

    update_data = {
        'name': 'Updated Name',
        'application_deadline': '2025-12-31 23:59:59'
    }

    with client:
        login_user(admin_user)
        
        # Test GET request
        response = client.get(url_for('admin.admin_stipend.edit', id=stipend.id))
        assert response.status_code == 200
        assert b"Edit Stipend" in response.data
        
        # Test POST with valid update
        response = client.post(
            url_for('admin.admin_stipend.edit', id=stipend.id),
            data=update_data,
            follow_redirects=True
        )
        assert response.status_code == 200
        assert FlashMessages.UPDATE_SUCCESS.value.encode() in response.data
        
        # Verify update
        updated_stipend = Stipend.query.get(stipend.id)
        assert updated_stipend.name == 'Updated Name'

def test_delete_stipend_route(client, admin_user, test_data):
    """Test stipend deletion through route handler"""
    stipend = Stipend(**test_data)
    db.session.add(stipend)
    db.session.commit()

    with client:
        login_user(admin_user)
        response = client.post(
            url_for('admin.admin_stipend.delete', id=stipend.id),
            follow_redirects=True
        )
        assert response.status_code == 200
        assert FlashMessages.DELETE_SUCCESS.value.encode() in response.data
        
        # Verify deletion
        deleted_stipend = Stipend.query.get(stipend.id)
        assert deleted_stipend is None

def test_stipend_routes_require_admin(client, regular_user):
    """Test that stipend routes require admin access"""
    routes = [
        ('admin.admin_stipend.create', 'GET'),
        ('admin.admin_stipend.create', 'POST'),
        ('admin.admin_stipend.edit', 'GET', {'id': 1}),
        ('admin.admin_stipend.edit', 'POST', {'id': 1}),
        ('admin.admin_stipend.delete', 'POST', {'id': 1})
    ]

    with client:
        login_user(regular_user)
        for route in routes:
            method = route[1]
            kwargs = route[2] if len(route) > 2 else {}
            response = getattr(client, method.lower())(
                url_for(route[0], **kwargs),
                follow_redirects=True
            )
            assert response.status_code == 403  # Forbidden

def test_stipend_create_with_missing_organization(client, admin_user, test_data):
    """Test stipend creation with missing organization"""
    # Remove organization_id from test data
    test_data.pop('organization_id', None)
    
    with client:
        login_user(admin_user)
        response = client.post(
            url_for('admin.admin_stipend.create'),
            data=test_data,
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b"Organization is required" in response.data

def test_stipend_edit_nonexistent(client, admin_user):
    """Test editing a non-existent stipend"""
    with client:
        login_user(admin_user)
        response = client.post(
            url_for('admin.admin_stipend.edit', id=9999),
            data={'name': 'Test'},
            follow_redirects=True
        )
        assert response.status_code == 200
        assert FlashMessages.NOT_FOUND.value.encode() in response.data

def test_stipend_delete_nonexistent(client, admin_user):
    """Test deleting a non-existent stipend"""
    with client:
        login_user(admin_user)
        response = client.post(
            url_for('admin.admin_stipend.delete', id=9999),
            follow_redirects=True
        )
        assert response.status_code == 200
        assert FlashMessages.NOT_FOUND.value.encode() in response.data

def test_stipend_pagination_edge_cases(client, admin_user, test_data):
    """Test pagination edge cases"""
    # Create 25 stipends
    for i in range(25):
        stipend = Stipend(**test_data)
        stipend.name = f"Test Stipend {i}"
        db.session.add(stipend)
    db.session.commit()

    with client:
        login_user(admin_user)
        
        # Test first page
        response = client.get(url_for('admin.admin_stipend.index'))
        assert response.status_code == 200
        
        # Test last page
        response = client.get(url_for('admin.admin_stipend.index', page=3))
        assert response.status_code == 200
        
        # Test out of bounds page
        response = client.get(url_for('admin.admin_stipend.index', page=999))
        assert response.status_code == 200
        assert b"Test Stipend 24" in response.data  # Should redirect to last page

def test_stipend_create_rate_limiting(client, admin_user, test_data):
    """Test rate limiting on stipend creation"""
    org = Organization(name="Test Org")
    db.session.add(org)
    db.session.commit()
    test_data['organization_id'] = org.id

    with client:
        login_user(admin_user)
        
        # Make 11 requests (limit is 10 per minute)
        for i in range(11):
            response = client.post(
                url_for('admin.admin_stipend.create'),
                data=test_data,
                follow_redirects=True
            )
            
        # Last request should be rate limited
        assert response.status_code == 429

def test_htmx_create_stipend(client, admin_user, test_data):
    """Test HTMX partial response for stipend creation"""
    org = Organization(name="Test Org")
    db.session.add(org)
    db.session.commit()
    test_data['organization_id'] = org.id

    with client:
        login_user(admin_user)
        
        # Add HTMX headers
        headers = {
            'HX-Request': 'true',
            'HX-Trigger': 'stipendForm'
        }
        
        response = client.post(
            url_for('admin.admin_stipend.create'),
            data=test_data,
            headers=headers,
            follow_redirects=True
        )
        
        # Verify HTMX response
        assert response.status_code == 200
        assert 'HX-Trigger' in response.headers
        assert 'stipendCreated' in response.headers['HX-Trigger']

def test_htmx_validation_errors(client, admin_user):
    """Test HTMX response for form validation errors"""
    invalid_data = {
        'name': '',  # Invalid name
        'application_deadline': 'invalid-date'
    }

    with client:
        login_user(admin_user)
        
        # Add HTMX headers
        headers = {
            'HX-Request': 'true',
            'HX-Trigger': 'stipendForm'
        }
        
        response = client.post(
            url_for('admin.admin_stipend.create'),
            data=invalid_data,
            headers=headers,
            follow_redirects=True
        )
        
        # Verify HTMX error response
        assert response.status_code == 200
        assert 'HX-Trigger' in response.headers
        assert 'validationError' in response.headers['HX-Trigger']
        assert b"Name: This field is required" in response.data

def test_database_constraint_violation(client, admin_user, test_data):
    """Test handling of database constraint violations"""
    org = Organization(name="Test Org")
    db.session.add(org)
    db.session.commit()
    test_data['organization_id'] = org.id

    # Create initial stipend
    stipend = Stipend(**test_data)
    db.session.add(stipend)
    db.session.commit()

    with client:
        login_user(admin_user)
        
        # Try to create duplicate stipend
        response = client.post(
            url_for('admin.admin_stipend.create'),
            data=test_data,
            follow_redirects=True
        )
        
        # Verify constraint violation handling
        assert response.status_code == 200
        assert FlashMessages.CREATE_ERROR.value.encode() in response.data

def test_missing_required_fields(client, admin_user):
    """Test handling of missing required fields"""
    invalid_data = {
        'name': '',  # Missing required field
        'application_deadline': ''  # Missing required field
    }

    with client:
        login_user(admin_user)
        response = client.post(
            url_for('admin.admin_stipend.create'),
            data=invalid_data,
            follow_redirects=True
        )
        
        # Verify error handling
        assert response.status_code == 200
        assert b"Name: This field is required" in response.data
        assert b"Application Deadline: This field is required" in response.data

def test_invalid_form_submission(client, admin_user):
    """Test handling of completely invalid form data"""
    invalid_data = {
        'name': 'A' * 101,  # Exceeds max length
        'application_deadline': 'not-a-date'
    }

    with client:
        login_user(admin_user)
        response = client.post(
            url_for('admin.admin_stipend.create'),
            data=invalid_data,
            follow_redirects=True
        )
        
        # Verify error handling
        assert response.status_code == 200
        assert b"Name: Field must be between 1 and 100 characters long" in response.data
        assert b"Application Deadline: Invalid date format" in response.data
