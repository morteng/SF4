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
