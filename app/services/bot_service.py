from app.models.bot import Bot
from app.extensions import db
from app.models.notification import Notification  # Import the Notification model

def create_bot(data):
    bot = Bot(name=data['name'], description=data['description'], status=data['status'])
    db.session.add(bot)
    db.session.commit()
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
