import pytest

@pytest.mark.usefixtures("admin_user")
def test_create_bot_authorized(test_client, admin_token):
    # Use the session cookie directly in the headers
    response = test_client.post('/admin/bots', json={
        'name': 'TestBot',
        'description': 'A test bot',
        'status': 'active'
    }, headers={'Cookie': admin_token})
    logging.info(f"Response status code: {response.status_code}")
    assert response.status_code == 201
