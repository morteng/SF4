from app.models.bot import Bot
from app.models.notification import Notification
from app.extensions import db

def create_bot(name, description, status):
    bot = Bot(name=name, description=description, status=status)
    return bot

def get_bot_by_id(bot_id):
    return db.session.get(Bot, bot_id)

def run_bot(bot):
    # Implement the logic to run the bot here
    # For now, just update its status
    bot.status = 'running'
    db.session.commit()

def get_all_bots():
    return db.session.query(Bot).all()

def update_bot(bot, data):
    bot.name = data['name']
    bot.description = data['description']
    # Update other fields as necessary
    db.session.commit()

def delete_bot(bot):
    db.session.delete(bot)
    db.session.commit()

def get_recent_logs(limit=5):
    return Notification.query.order_by(Notification.created_at.desc()).limit(limit).all()
