import pytest
from flask import url_for
from app.models.bot import Bot
from tests.conftest import extract_csrf_token
from app.constants import FLASH_MESSAGES, FLASH_CATEGORY_SUCCESS, FLASH_CATEGORY_ERROR

@pytest.fixture(scope='function')
def bot_data():
    return {
        'name': 'Test Bot',
        'description': 'This is a test bot.',
        'status': True
    }

@pytest.fixture(scope='function')
def test_bot(db_session, bot_data):
    """Provide a test bot."""
    bot = Bot(**bot_data)
    db_session.add(bot)
    db_session.commit()
    yield bot
    db_session.delete(bot)
    db_session.commit()

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
    # Assert the flash message
    assert FLASH_MESSAGES["CREATE_BOT_SUCCESS"].encode() in response.data

def test_create_bot_route_with_invalid_data(logged_in_admin, bot_data):
    create_response = logged_in_admin.get(url_for('admin.bot.create'))
    assert create_response.status_code == 200

    csrf_token = extract_csrf_token(create_response.data)
    invalid_data = {
        'name': '',  # Invalid name
        'description': bot_data['description'],
        'status': bot_data['status'],
        'csrf_token': csrf_token
    }
    response = logged_in_admin.post(url_for('admin.bot.create'), data=invalid_data, follow_redirects=True)

    assert response.status_code == 200
    bots = Bot.query.all()
    assert not any(bot.name == '' for bot in bots)  # Ensure no bot with an empty name was created
    # Assert the flash message
    assert FLASH_MESSAGES["CREATE_BOT_ERROR"].encode() in response.data

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
    # Assert the flash message
    assert FLASH_MESSAGES["UPDATE_BOT_SUCCESS"].encode() in response.data

def test_update_bot_route_with_invalid_id(logged_in_admin):
    update_response = logged_in_admin.get(url_for('admin.bot.update', id=9999))
    assert update_response.status_code == 302
    assert url_for('admin.bot.index', _external=False) == update_response.headers['Location']

def test_delete_bot_route(logged_in_admin, test_bot, db_session):
    # Perform the DELETE operation
    delete_response = logged_in_admin.post(url_for('admin.bot.delete', id=test_bot.id))
    assert delete_response.status_code == 302
    
    # Ensure the bot is no longer in the session after deleting
    db_session.expire_all()
    updated_bot = db_session.get(Bot, test_bot.id)
    assert updated_bot is None
    # Assert the flash message
    assert FLASH_MESSAGES["DELETE_BOT_SUCCESS"].encode() in delete_response.data

def test_delete_bot_route_with_invalid_id(logged_in_admin):
    delete_response = logged_in_admin.post(url_for('admin.bot.delete', id=9999))
    assert delete_response.status_code == 302
    assert url_for('admin.bot.index', _external=False) == delete_response.headers['Location']

def test_create_bot_route_with_database_error(logged_in_admin, bot_data, db_session, monkeypatch):
    with logged_in_admin.application.app_context():
        data = bot_data

        def mock_commit(*args, **kwargs):
            raise Exception("Database error")
            
        monkeypatch.setattr(db_session, 'commit', mock_commit)
        
        response = logged_in_admin.post(url_for('admin.bot.create'), data=data)
        
        assert response.status_code == 200
        assert FLASH_MESSAGES["CREATE_BOT_ERROR"].encode() in response.data  # Confirm error message is present

        bots = Bot.query.all()
        assert not any(bot.name == data['name'] for bot in bots)  # Ensure no bot was created
