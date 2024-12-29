import pytest
from datetime import datetime, timedelta
from app.models.bot import Bot
from app.utils import calculate_next_run

@pytest.fixture
def bot():
    return Bot(name="TestBot", description="A test bot")

def test_bot_creation(bot):
    assert bot.name == "TestBot"
    assert bot.status == "inactive"
    assert bot.is_active is True

def test_calculate_next_run():
    schedule = "0 0 * * *"  # Daily at midnight
    next_run = calculate_next_run(schedule)
    assert isinstance(next_run, datetime)
    assert next_run > datetime.now()

def test_bot_run(bot):
    bot.status = "running"
    assert bot.status == "running"
    assert bot.last_run is not None
