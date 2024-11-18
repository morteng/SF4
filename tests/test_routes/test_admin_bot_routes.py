import pytest

@pytest.fixture(scope='module')
def client(test_client):
    return test_client

def test_create_bot_unauthorized(client):
    """Test creating bot without authentication fails"""
    response = client.post('/admin/bots', json={
        'name': 'Test Bot',
        'description': 'Test Description',
        'status': 'active'
    })
    assert response.status_code == 302

def test_create_bot_authorized(client, admin_token):
    """Test creating bot with authentication succeeds"""
    client.cookie_jar.update(admin_token)
    response = client.post('/admin/bots', json={
        'name': 'Test Bot',
        'description': 'Test Description',
        'status': 'active'
    })
    assert response.status_code == 201
