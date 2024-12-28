from datetime import datetime, timezone
from abc import abstractmethod
from app.extensions import db

from datetime import datetime, timezone
from abc import abstractmethod
from app.extensions import db
from app.models.notification import Notification, NotificationType
from app.models.audit_log import AuditLog
from flask import current_app

class BaseBot:
    """Base class for all bots"""
    def __init__(self):
        self.status = 'idle'
        self.last_run = None
        self.error_log = None
        self.start_time = None
        self.end_time = None
        self.execution_time = None
        
    def run(self):
        """Execute the bot with proper status tracking"""
        try:
            self.status = 'running'
            self.start_time = datetime.now(timezone.utc)
            self.execute()
            self.status = 'completed'
        except Exception as e:
            self.status = 'error'
            self.error_log = str(e)
            raise
        finally:
            self.end_time = datetime.now(timezone.utc)
            self.execution_time = (self.end_time - self.start_time).total_seconds()
            self._log_execution()
            
    def _log_execution(self):
        """Log bot execution details"""
        current_app.logger.info(
            f"Bot {self.__class__.__name__} executed in {self.execution_time:.2f} seconds. "
            f"Status: {self.status}"
        )
            
    @abstractmethod
    def execute(self):
        """Main bot logic to be implemented by subclasses"""
        pass

class Bot(db.Model, BaseBot):
    __mapper_args__ = {"confirm_deleted_rows": False}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='inactive')
    last_run = db.Column(db.DateTime, nullable=True)
    error_log = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<Bot {self.name}>"

    @property
    def status_enum(self):
        """Get status as enum value"""
        from app.constants import BotStatus
        return BotStatus(self.status)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'error_log': self.error_log,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active
        }
