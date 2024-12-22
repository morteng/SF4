# tests/test_bot_routes.py

import pytest
from flask import url_for, session
from app.models.bot import Bot
from app.services.bot_service import create_bot, delete_bot, get_bot_by_id
from app.utils import flash_message  # Import the new utility function

@pytest.fixture
def bot_data():
    return {
        'name': 'Test Bot',
        'description': 'A test bot for testing purposes'
    }

def test_create_bot(client, bot_data):
    response = client.post(url_for('admin.bot.create'), data=bot_data)
    assert response.status_code == 302
    # Check if the flash message is set correctly
    with client.session_transaction() as sess:
        flash_messages = sess['_flashes']
        assert len(flash_messages) == 1
        category, message = flash_messages[0]
        assert category == 'success'
        assert message == "Bot created successfully."

def test_delete_bot(client):
    bot = create_bot(bot_data)
    response = client.post(url_for('admin.bot.delete', id=bot.id))
    assert response.status_code == 302
    # Check if the flash message is set correctly
    with client.session_transaction() as sess:
        flash_messages = sess['_flashes']
        assert len(flash_messages) == 1
        category, message = flash_messages[0]
        assert category == 'success'
        assert message == "Bot deleted successfully."

def test_edit_bot(client, bot_data):
    bot = create_bot(bot_data)
    updated_data = {
        'name': 'Updated Bot',
        'description': 'An updated test bot for testing purposes'
    }
    response = client.post(url_for('admin.bot.edit', id=bot.id), data=updated_data)
    assert response.status_code == 302
    # Check if the flash message is set correctly
    with client.session_transaction() as sess:
        flash_messages = sess['_flashes']
        assert len(flash_messages) == 1
        category, message = flash_messages[0]
        assert category == 'success'
        assert message == "Bot updated successfully."
