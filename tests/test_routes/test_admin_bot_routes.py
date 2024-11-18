import pytest

@pytest.mark.usefixtures("admin_user")
def test_create_bot_authorized(test_client, admin_token):
    headers = {
        'Authorization': f'Bearer {admin_token}'
    }
    response = test_client.post('/bots', data={
        'name': 'TestBot',
        'description': 'A test bot'
    }, headers=headers)
    assert response.status_code == 201
    # Add more assertions as needed to validate the response
