import pytest
from flask import url_for

@pytest.fixture(scope='module')
def admin_token(test_client, admin_user):
    with test_client:
        response = test_client.post(url_for('public_user.login'), data={
            'username': admin_user.username,
            'password': 'securepassword'
        }, follow_redirects=True)
        assert response.status_code == 200
        return test_client.cookie_jar

def test_create_bot_unauthorized(client):
    """Test creating bot without authentication fails"""
    response = client.post('/admin/api/bots', json={  # Updated to /admin/api/bots
        'name': 'Test Bot',
        'description': 'Test Description',
        'status': 'active'
    })
    assert response.status_code == 401

def test_create_bot_authorized(client, admin_token):
    """Test creating bot with authentication succeeds"""
    client.cookie_jar.update(admin_token)
    response = client.post('/admin/api/bots', json={  # Updated to /admin/api/bots
        'name': 'Test Bot',
        'description': 'Test Description',
        'status': 'active'
    })
    assert response.status_code == 201
