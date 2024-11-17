import pytest
from bots.tag_bot import TagBot

def test_tag_bot_initialization():
    tag_bot = TagBot()
    assert tag_bot.name == "TagBot"
    assert tag_bot.description == "Automatically tags stipends based on content."
    assert tag_bot.status == "inactive"

def test_tag_bot_run():
    tag_bot = TagBot()
    tag_bot.run()
    assert tag_bot.status == "active"
