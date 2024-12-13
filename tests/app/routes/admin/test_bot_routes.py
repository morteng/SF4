import pytest
from flask import url_for
from app.models.bot import Bot
from tests.conftest import extract_csrf_token

@pytest.fixture(scope='function')
def bot_data():
    return {
        'name': 'Test Bot',
        'description': 'A test bot for testing purposes.',
        'status': 'inactive'
    }

@pytest.fixture(scope='function')
def test_bot(db_session, bot_data):
    bot = Bot(**bot_data)
    db_session.add(bot)
    db_session.commit()
    yield bot

    # Teardown: Attempt to delete the bot and rollback if an error occurs
    try:
        db_session.delete(bot)
        db_session.commit()
    except Exception as e:
        print(f"Failed to delete test bot during teardown: {e}")
        db_session.rollback()

def test_create_bot_route(logged_in_admin, bot_data):
    create_response = logged_in_admin.get(url_for('admin.bot.create'))
    assert create_response.status_code == 200

    csrf_token = extract_csrf_token(create_response.data)
    response = logged_in_admin.post(url_for('admin.bot.create'), data={
        'name': bot_data['name'],
        'description': bot_data['description'],
        'status': bot_data['status'],
        'csrf_token': csrf_token
    }, follow_redirects=True)

    assert response.status_code == 200
    bots = Bot.query.all()
    assert any(bot.name == bot_data['name'] and bot.description == bot_data['description'] for bot in bots)

def test_delete_bot_route(logged_in_admin, test_bot, db_session):
    # Perform the DELETE operation
    delete_response = logged_in_admin.post(url_for('admin.bot.delete', id=test_bot.id))
    assert delete_response.status_code == 302
    
    # Ensure the bot is no longer in the session after deleting
    db_session.expire_all()
    updated_bot = db_session.get(Bot, test_bot.id)
    assert updated_bot is None

def test_update_bot_route(logged_in_admin, test_bot, db_session):
    update_response = logged_in_admin.get(url_for('admin.bot.update', id=test_bot.id))
    assert update_response.status_code == 200

    csrf_token = extract_csrf_token(update_response.data)
    updated_data = {
        'name': 'Updated Bot Name',
        'description': test_bot.description,
        'status': test_bot.status,
        'csrf_token': csrf_token
    }
    response = logged_in_admin.post(url_for('admin.bot.update', id=test_bot.id), data=updated_data, follow_redirects=True)

    assert response.status_code == 200
    updated_bot = db_session.get(Bot, test_bot.id)  # Use db_session.get to retrieve the bot
    assert updated_bot.name == 'Updated Bot Name'
