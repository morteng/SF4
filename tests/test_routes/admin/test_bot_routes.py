import pytest

@pytest.mark.usefixtures('client', 'session')
def test_create_bot_authorized(client, session):
    # Your test code here
    response = client.post('/admin/bots/create', data={
        'name': 'TestBot',
        'description': 'A test bot',
        'status': 'active'
    })
    assert response.status_code == 200
