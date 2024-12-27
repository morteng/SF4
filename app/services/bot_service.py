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

from datetime import datetime
from app.models.notification import Notification, NotificationType

def run_bot(bot):
    try:
        bot.status = 'running'
        bot.last_run = datetime.utcnow()
        
        # Add bot-specific logic here
        if bot.name == 'TagBot':
            # Implement tagging logic
            pass
        elif bot.name == 'UpdateBot':
            # Implement update logic
            pass
        elif bot.name == 'ReviewBot':
            # Implement review logic
            pass
            
        bot.status = 'completed'
        Notification.create(
            type=NotificationType.BOT_SUCCESS,
            message=f"{bot.name} completed successfully"
        )
    except Exception as e:
        bot.status = 'failed'
        Notification.create(
            type=NotificationType.BOT_ERROR,
            message=f"{bot.name} failed: {str(e)}"
        )
    finally:
        db.session.commit()

def get_all_bots():
    return db.session.query(Bot).all()

def update_bot(bot, data):
    bot.name = data['name']
    bot.description = data['description']
    # Update other fields as necessary
    db.session.commit()
    return bot  # Add this line to return the updated bot

def delete_bot(bot):
    db.session.delete(bot)
    db.session.commit()

def get_recent_logs(limit=5):
    return Notification.query.order_by(Notification.created_at.desc()).limit(limit).all()
