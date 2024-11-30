import pytest
from bs4 import BeautifulSoup

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
    # First, get the form page to obtain CSRF token
    response = logged_in_client.get('/admin/organizations/create')
    assert response.status_code == 200

    # Extract CSRF token from form
    soup = BeautifulSoup(response.data.decode(), 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']

    # Now, create the organization with CSRF token
    response = logged_in_client.post('/admin/organizations/create', json={
        'csrf_token': csrf_token,
        'name': 'Test Organization',
        'description': 'Test Description',
        'homepage_url': 'http://test.org'
    })
    assert response.status_code == 201
    assert 'id' in response.json

# Other test functions remain unchanged
