import pytest

@pytest.mark.usefixtures("admin_user")
def test_create_bot_authorized(test_client, admin_token):
    # Use the session cookie directly in the headers
    response = test_client.post('/api/bots', json={
        'name': 'TestBot',
        'description': 'A test bot',
        'status': 'active'
    }, headers={'Cookie': admin_token})
    assert response.status_code == 201

@pytest.mark.usefixtures("admin_user")
def test_create_bot_unauthorized(test_client):
    # Make the request without any token
    response = test_client.post('/api/bots', json={
        'name': 'TestBot',
        'description': 'A test bot',
        'status': 'active'
    })
    assert response.status_code == 401
