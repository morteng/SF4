from app.models.bot import Bot
from app.extensions import db

def get_all_bots():
    return Bot.query.all()

def get_bot_by_id(bot_id):
    return Bot.query.get(bot_id)

def create_bot(name, description='', status='inactive'):
    bot = Bot(name=name, description=description, status=status)
    db.session.add(bot)
    db.session.commit()
    return bot

def update_bot(bot_id, name=None, description=None, status=None):
    bot = get_bot_by_id(bot_id)
    if not bot:
        raise ValueError("Bot not found")
    
    if name is not None:
        bot.name = name
    if description is not None:
        bot.description = description
    if status is not None:
        bot.status = status
    
    db.session.commit()
    return bot

def delete_bot(bot_id):
    bot = get_bot_by_id(bot_id)
    if not bot:
        raise ValueError("Bot not found")
    
    db.session.delete(bot)
    db.session.commit()
