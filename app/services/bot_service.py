from app.models.bot import Bot, BotStatus, BotSchedule
from app.services.base_service import BaseService
from app.extensions import db
from app.models.notification import Notification
from datetime import datetime

class BotService(BaseService):
    def __init__(self):
        super().__init__(Bot)
        # Add bot specific validation rules
        self.validation_rules = {
            'name': {'required': True, 'max_length': 100},
            'description': {'required': True},
            'schedule': {'choices': ['daily', 'weekly', 'monthly']}
        }
        
    def get_form_choices(self):
        return {
            'status': [(status.value, status.name) for status in BotStatus],
            'schedule': [('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')]
        }

    def validate_form_data(self, data):
        """Add bot specific validation"""
        errors = {}
        for field, rules in self.validation_rules.items():
            if rules.get('required') and not data.get(field):
                errors[field] = f"{field} is required"
            if rules.get('max_length') and len(data.get(field, '')) > rules['max_length']:
                errors[field] = f"{field} must be less than {rules['max_length']} characters"
            if rules.get('choices') and data.get(field) not in rules['choices']:
                errors[field] = f"{field} must be one of {', '.join(rules['choices'])}"
        return errors

    def create(self, data, user_id=None):
        """Create a new bot with validation"""
        errors = self.validate_form_data(data)
        if errors:
            raise ValueError("\n".join(errors.values()))
            
        bot = Bot(
            name=data['name'],
            description=data['description'],
            status=BotStatus.INACTIVE,
            schedule=data.get('schedule'),
            is_active=data.get('is_active', True)
        )
        
        if bot.schedule:
            bot.next_run = bot.calculate_next_run()
            bot.status = BotStatus.SCHEDULED
            
        db.session.add(bot)
        db.session.commit()
        return bot

    def get_by_id(self, bot_id):
        return db.session.get(Bot, bot_id)

from datetime import datetime
from flask import request
from flask_login import current_user
from app.models.notification import Notification, NotificationType
from app.models.audit_log import AuditLog

def run_bot(bot):
    try:
        bot.status = 'running'
        bot.last_run = datetime.utcnow()
        bot.last_error = None
        db.session.commit()
        
        # Create audit log
        AuditLog.create(
            user_id=current_user.id if current_user.is_authenticated else 0,
            action=f'run_bot_{bot.name}',
            object_type='Bot',
            object_id=bot.id,
            ip_address=request.remote_addr
        )
        
        # Run the appropriate bot
        if bot.name == 'TagBot':
            from bots.tag_bot import TagBot
            TagBot().run()
        elif bot.name == 'UpdateBot':
            from bots.update_bot import UpdateBot
            UpdateBot().run()
        elif bot.name == 'ReviewBot':
            from bots.review_bot import ReviewBot
            ReviewBot().run()
        else:
            raise ValueError(f"Unknown bot type: {bot.name}")
            
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

def calculate_next_run(schedule):
    """Calculate next run time based on schedule string"""
    from datetime import datetime, timedelta
    now = datetime.utcnow()
    
    if schedule == 'daily':
        return now + timedelta(days=1)
    elif schedule == 'weekly':
        return now + timedelta(weeks=1)
    elif schedule == 'monthly':
        return now + timedelta(days=30)
    else:
        raise ValueError("Invalid schedule")
from app.models import Bot, AuditLog
from app.extensions import db
from datetime import datetime

class TagBot:
    def run(self):
        bot = Bot(name='TagBot', status='running', last_run=datetime.utcnow())
        db.session.add(bot)
        
        try:
            # Implement tagging logic
            pass
        except Exception as e:
            bot.error_log = str(e)
            bot.status = 'failed'
        finally:
            db.session.commit()

class UpdateBot:
    def run(self):
        bot = Bot(name='UpdateBot', status='running', last_run=datetime.utcnow())
        db.session.add(bot)
        
        try:
            # Implement update logic
            pass
        except Exception as e:
            bot.error_log = str(e)
            bot.status = 'failed'
        finally:
            db.session.commit()

class ReviewBot:
    def run(self):
        bot = Bot(name='ReviewBot', status='running', last_run=datetime.utcnow())
        db.session.add(bot)
        
        try:
            # Implement review logic
            pass
        except Exception as e:
            bot.error_log = str(e)
            bot.status = 'failed'
        finally:
            db.session.commit()
