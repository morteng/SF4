from app.models.bot import Bot
from app.extensions import db  # Import db from extensions

def get_bot_by_id(bot_id):
    """Retrieve a bot by its ID."""
    try:
        return Bot.query.get(bot_id)
    except Exception as e:
        print(f"Failed to retrieve bot with ID {bot_id}: {e}")
        return None

def update_bot_status(bot_id, status):
    """Update the status of a bot."""
    try:
        bot = get_bot_by_id(bot_id)
        if bot:
            bot.status = status
            db.session.commit()
            return True
        return False
    except Exception as e:
        print(f"Failed to update bot status for ID {bot_id}: {e}")
        return False

def create_bot(name, description, status):
    """Create a new bot."""
    try:
        bot = Bot(name=name, description=description, status=status)
        db.session.add(bot)
        db.session.commit()
        return bot
    except Exception as e:
        print(f"Failed to create bot: {e}")
        return None

def list_all_bots():
    """List all bots in the database."""
    try:
        return Bot.query.all()
    except Exception as e:
        print(f"Failed to list bots: {e}")
        return []
