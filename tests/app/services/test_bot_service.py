import pytest
from app.models.bot import Bot
from app.services.bot_service import BotService

@pytest.fixture(scope='function')
def bot_data():
    return {
        'name': 'Test Bot',
        'description': 'A test bot for testing purposes.',
        'status': 'inactive'
    }

@pytest.fixture(scope='function')
def test_bot(db_session, bot_data):
    bot_service = BotService()
    bot = bot_service.create(bot_data)
    yield bot

    # Teardown: Attempt to delete the bot and rollback if an error occurs
    try:
        db_session.delete(bot)
        db_session.commit()
    except Exception as e:
        print(f"Failed to delete test bot during teardown: {e}")
        db_session.rollback()

def test_create_bot(db_session, bot_data):
    bot_service = BotService()
    bot = bot_service.create(bot_data)
    assert bot.name == bot_data['name']
    assert bot.description == bot_data['description']
    assert bot.status == bot_data['status']

def test_create_bot_missing_name(db_session, bot_data):
    del bot_data['name']
    bot_service = BotService()
    with pytest.raises(ValueError) as exc_info:
        bot_service.create(bot_data)
    assert "Bot name is required" in str(exc_info.value)

def test_create_bot_missing_description(db_session, bot_data):
    del bot_data['description']
    bot_service = BotService()
    with pytest.raises(ValueError) as exc_info:
        bot_service.create(bot_data)
    assert "Bot description is required" in str(exc_info.value)

def test_bot_status_enum(test_bot):
    from app.constants import BotStatus
    assert test_bot.status_enum == BotStatus.INACTIVE

def test_get_bot_by_id(test_bot):
    bot_service = BotService()
    retrieved_bot = bot_service.get_by_id(test_bot.id)
    assert retrieved_bot.id == test_bot.id
    assert retrieved_bot.name == test_bot.name

def test_update_bot(db_session, test_bot):
    bot_service = BotService()
    updated_data = {
        'name': 'Updated Bot Name',
        'description': test_bot.description,
        'status': test_bot.status
    }
    updated_bot = bot_service.update(test_bot, updated_data)
    assert updated_bot.name == 'Updated Bot Name'
