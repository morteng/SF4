import pytest
import logging
from flask import url_for
from app.models.bot import Bot
from tests.conftest import extract_csrf_token
from app.constants import FlashMessages, FlashCategory
from tests.utils import assert_flash_message, create_bot_data

@pytest.fixture(scope='function')
def bot_data():
    logging.info("Creating bot test data")
    return create_bot_data()

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
        'status': 'true' if bot_data['status'] else 'false',
        'csrf_token': csrf_token
    }, follow_redirects=True)

    assert response.status_code == 200
    bots = Bot.query.all()
    assert any(bot.name == bot_data['name'] and bot.description == bot_data['description'] for bot in bots)
    assert_flash_message(response, FlashMessages.CREATE_BOT_SUCCESS)

def test_create_bot_route_with_invalid_data(logged_in_admin, bot_data):
    create_response = logged_in_admin.get(url_for('admin.bot.create'))
    assert create_response.status_code == 200

    csrf_token = extract_csrf_token(create_response.data)
    invalid_data = {
        'name': '',  # Invalid name
        'description': bot_data['description'],
        'status': 'invalid_status',  # Explicit invalid value
        'csrf_token': csrf_token
    }
    response = logged_in_admin.post(url_for('admin.bot.create'), data=invalid_data, follow_redirects=True)

    assert response.status_code == 400
    bots = Bot.query.all()
    assert not any(bot.name == '' for bot in bots)  # Ensure no bot with an empty name was created
    # Assert the flash message using constants
    assert_flash_message(response, FlashMessages.CREATE_BOT_INVALID_DATA)

def test_update_bot_route(logged_in_admin, test_bot, db_session):
    update_response = logged_in_admin.get(url_for('admin.bot.edit', id=test_bot.id))
    assert update_response.status_code == 200

    csrf_token = extract_csrf_token(update_response.data)
    updated_data = {
        'name': 'Updated Bot Name',
        'description': test_bot.description,
        'status': 'true' if test_bot.status else 'false',  # Convert boolean to string
        'csrf_token': csrf_token
    }
    response = logged_in_admin.post(url_for('admin.bot.edit', id=test_bot.id), data={
        'name': updated_data['name'],
        'description': updated_data['description'],
        'status': updated_data['status'],  # Directly pass the value
        'csrf_token': csrf_token
    }, follow_redirects=True)

    assert response.status_code == 200
    updated_bot = db_session.get(Bot, test_bot.id)  # Use db_session.get to retrieve the bot
    assert updated_bot.name == 'Updated Bot Name'
    # Assert the flash message using constants
    assert_flash_message(response, FlashMessages.UPDATE_BOT_SUCCESS)

def test_update_bot_route_with_invalid_id(logged_in_admin):
    update_response = logged_in_admin.get(url_for('admin.bot.edit', id=9999))
    assert update_response.status_code == 302
    assert url_for('admin.bot.index', _external=False) == update_response.headers['Location']

def test_delete_bot_route(logged_in_admin, test_bot, db_session):
    # Perform the DELETE operation
    delete_response = logged_in_admin.post(
        url_for('admin.bot.delete', id=test_bot.id),
        follow_redirects=True  # Follow the redirect to capture flash messages
    )
    assert delete_response.status_code == 200  # After following redirects, status should be 200
    
    # Ensure the bot is no longer in the session after deleting
    db_session.expire_all()
    updated_bot = db_session.get(Bot, test_bot.id)
    assert updated_bot is None
    # Assert the flash message using constants
    assert_flash_message(delete_response, FlashMessages.DELETE_BOT_SUCCESS)

def test_delete_bot_route_with_invalid_id(logged_in_admin):
    delete_response = logged_in_admin.post(url_for('admin.bot.delete', id=9999))
    assert delete_response.status_code == 302
    assert url_for('admin.bot.index', _external=False) == delete_response.headers['Location']

def test_run_bot_success(logged_in_admin, test_bot, db_session, mocker):
    # Mock bot execution
    mock_bot = mocker.MagicMock()
    mock_bot.status = 'completed'
    mock_bot.error_log = None
    mock_bot.run = mocker.MagicMock()
    
    # Patch bot creation
    mocker.patch('bots.tag_bot.TagBot', return_value=mock_bot)
    
    response = logged_in_admin.post(url_for('admin.bot.run', id=test_bot.id))
    
    assert response.status_code == 302
    assert url_for('admin.bot.index', _external=False) == response.headers['Location']
    
    # Verify bot status was updated
    updated_bot = db_session.get(Bot, test_bot.id)
    assert updated_bot.status == 'completed'
    assert updated_bot.last_run is not None
    
    # Verify notification was created
    notification = Notification.query.filter_by(type=NotificationType.BOT_SUCCESS).first()
    assert notification is not None
    assert test_bot.name in notification.message

def test_run_bot_failure(logged_in_admin, test_bot, db_session, mocker):
    # Mock bot execution to raise an error
    mock_bot = mocker.MagicMock()
    mock_bot.run = mocker.MagicMock(side_effect=Exception("Test error"))
    
    # Patch bot creation
    mocker.patch('bots.tag_bot.TagBot', return_value=mock_bot)
    
    response = logged_in_admin.post(url_for('admin.bot.run', id=test_bot.id))
    
    assert response.status_code == 302
    assert url_for('admin.bot.index', _external=False) == response.headers['Location']
    
    # Verify bot status was updated
    updated_bot = db_session.get(Bot, test_bot.id)
    assert updated_bot.status == 'error'
    assert updated_bot.error_log == "Test error"
    
    # Verify notification was created
    notification = Notification.query.filter_by(type=NotificationType.BOT_ERROR).first()
    assert notification is not None
    assert "error" in notification.message.lower()

def test_run_bot_unknown_type(logged_in_admin, test_bot):
    test_bot.name = 'UnknownBot'
    db_session.commit()
    
    response = logged_in_admin.post(url_for('admin.bot.run', id=test_bot.id))
    
    assert response.status_code == 302
    assert url_for('admin.bot.index', _external=False) == response.headers['Location']
    assert_flash_message(response, FlashMessages.BOT_RUN_ERROR)

def test_run_bot_not_found(logged_in_admin):
    response = logged_in_admin.post(url_for('admin.bot.run', id=9999))
    
    assert response.status_code == 302
    assert url_for('admin.bot.index', _external=False) == response.headers['Location']
    assert_flash_message(response, FlashMessages.BOT_NOT_FOUND)
