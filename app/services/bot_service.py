from app.models.bot import Bot
from app.extensions import db

def list_all_bots():
    bots = Bot.query.all()
    return bots

def get_bot_by_id(bot_id):
    bot = Bot.query.get(bot_id)
    return bot

def update_bot(bot_id, name, description, status):
    bot = get_bot_by_id(bot_id)
    if bot:
        bot.name = name
        bot.description = description
        bot.status = status
        db.session.commit()
        return True
    return False
