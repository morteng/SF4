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
    # Validate the response content
    assert b'bot_id' in response.data

    # Check if the bot was created in the database
    from app.models.bot import Bot
    with test_client.application.app_context():
        bot = Bot.query.filter_by(name='TestBot').first()
        assert bot is not None
        assert bot.description == 'A test bot'
        assert bot.status == 'active'

@pytest.mark.usefixtures("admin_user")
def test_create_bot_unauthorized(test_client):
    # Make the request without any token
    response = test_client.post('/api/bots', json={
        'name': 'TestBot',
        'description': 'A test bot',
        'status': 'active'
    })
    assert response.status_code == 401
