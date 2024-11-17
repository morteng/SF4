import pytest

def test_bot_status(client):
    response = client.get('/bot/status')
    assert response.status_code == 200
    assert b'"status": "All bots operational"' in response.data
