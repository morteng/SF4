import pytest

def test_create_organization_unauthorized(client):
    """Test creating organization without authentication fails"""
    response = client.post('/admin/organizations/create', json={
        'name': 'Test Organization',
        'description': 'Test Description',
        'homepage_url': 'http://test.org'
    })
    assert response.status_code == 401

def test_create_organization_authorized(logged_in_client):
    """Test creating organization with admin authentication succeeds"""
    response = logged_in_client.post('/admin/organizations/create', json={
        'name': 'Test Organization',
        'description': 'Test Description',
        'homepage_url': 'http://test.org'
    })
    assert response.status_code == 201
    assert 'organization_id' in response.json

def test_update_organization_authorized(logged_in_client):
    """Test updating organization with admin authentication"""
    # First create an organization to update
    create_response = logged_in_client.post('/admin/organizations/create', json={
        'name': 'Initial Organization',
        'description': 'Initial Description',
        'homepage_url': 'http://initial.org'
    })
    assert create_response.status_code == 201
    organization_id = create_response.json['organization_id']

    # Now update the organization
    response = logged_in_client.put(f'/admin/organizations/{organization_id}', json={
        'name': 'Updated Organization',
        'description': 'Updated Description',
        'homepage_url': 'http://updated.org'
    })
    assert response.status_code == 200
    assert response.json['organization_id'] == organization_id

def test_delete_organization_authorized(logged_in_client):
    """Test deleting organization with admin authentication"""
    # First create an organization to delete
    create_response = logged_in_client.post('/admin/organizations/create', json={
        'name': 'Organization to Delete',
        'description': 'Description of Organization to Delete',
        'homepage_url': 'http://delete.org'
    })
    assert create_response.status_code == 201
    organization_id = create_response.json['organization_id']

    # Now delete the organization
    response = logged_in_client.delete(f'/admin/organizations/{organization_id}')
    assert response.status_code == 200
    assert response.json['organization_id'] == organization_id

def test_create_organization_missing_fields(logged_in_client):
    """Test creating organization with missing fields fails"""
    response = logged_in_client.post('/admin/organizations/create', json={
        'name': 'Test Organization',
        'homepage_url': 'http://test.org'
    })
    assert response.status_code == 400

def test_create_organization_invalid_name(logged_in_client):
    """Test creating organization with invalid name fails"""
    response = logged_in_client.post('/admin/organizations/create', json={
        'name': '',
        'description': 'Test Description',
        'homepage_url': 'http://test.org'
    })
    assert response.status_code == 400

def test_create_organization_invalid_homepage_url(logged_in_client):
    """Test creating organization with invalid homepage URL fails"""
    response = logged_in_client.post('/admin/organizations/create', json={
        'name': 'Test Organization',
        'description': 'Test Description',
        'homepage_url': 'invalid-url'
    })
    assert response.status_code == 400
