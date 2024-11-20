from app.models.bot import Bot

def get_bot_by_id(bot_id):
    return Bot.query.get(bot_id)

def run_bot(bot):
    # Logic to run the bot
    pass

def get_all_bots():
    return Bot.query.all()
