from app.models.bot import Bot

def get_bot_by_id(bot_id):
    from app.extensions import db
    return db.session.get(Bot, bot_id)

def update_bot_status(bot_id, status):
    from app.extensions import db
    bot = get_bot_by_id(bot_id)
    if bot:
        bot.status = status
        db.session.commit()
        return True
    return False
