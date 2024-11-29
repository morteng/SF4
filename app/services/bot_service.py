from app.models.bot import Bot

def create_bot(name, description, status):
    bot = Bot(name=name, description=description, status=status)
    return bot
