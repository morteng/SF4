import pytest

@pytest.mark.usefixtures("admin_user")
def test_create_bot_authorized(client, admin_token):
    with client.application.app_context():
        response = client.post('/api/bots', json={
            'name': 'TestBot',
            'description': 'A test bot',
            'status': 'active'
        }, headers={'Cookie': admin_token})
        assert response.status_code == 201
        assert b'bot_id' in response.data

        from app.models.bot import Bot
        with client.application.app_context():
            bot = Bot.query.filter_by(name='TestBot').first()
            assert bot is not None
            assert bot.description == 'A test bot'
            assert bot.status == 'active'

@pytest.mark.usefixtures("admin_user")
def test_create_bot_unauthorized(client):
    response = client.post('/api/bots', json={
        'name': 'TestBot',
        'description': 'A test bot',
        'status': 'active'
    })
    assert response.status_code == 401
