from app.models.bot import Bot

class BotService:
    def __init__(self):
        pass

    @staticmethod
    def get_bot_by_id(bot_id):
        from app.extensions import db
        return db.session.query(Bot).filter_by(id=bot_id).first()
