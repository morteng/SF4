import pytest

def test_create_organization_unauthorized(client, db):
    """Test creating organization without authentication fails"""
    response = client.post('/admin/organizations/create', json={
        'name': 'Test Organization',
        'description': 'Test Description',
        'homepage_url': 'http://test.org'
    })
    assert response.status_code == 401

def test_create_organization_authorized(logged_in_client, db):
    """Test creating organization with admin authentication succeeds"""
    # First, ensure that the user is logged in by accessing a protected route
    response = logged_in_client.get('/admin/dashboard', follow_redirects=True)
    assert response.status_code == 200

    # Now, create the organization
    response = logged_in_client.post('/admin/organizations/create', json={
        'name': 'Test Organization',
        'description': 'Test Description',
        'homepage_url': 'http://test.org'
    })
    assert response.status_code == 201
    assert 'id' in response.json

# Other test functions remain unchanged
