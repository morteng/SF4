import pytest

@pytest.mark.usefixtures("admin_user")
def test_create_bot_authorized(test_client, admin_token):
    headers = {
        'Authorization': f'Bearer {admin_token}'
    }
    response = test_client.post('/bots', data={
        'name': 'TestBot',
        'description': 'A test bot',
        'status': 'active'
    }, headers=headers)
    assert response.status_code == 201
    # Validate the response content
    assert b'Bot created successfully' in response.data

    # Check if the bot was created in the database
    from app.models.bot import Bot
    with test_client.application.app_context():
        bot = Bot.query.filter_by(name='TestBot').first()
        assert bot is not None
        assert bot.description == 'A test bot'
        assert bot.status == 'active'
