from datetime import datetime, timezone, timedelta
from croniter import croniter
from app.extensions import db

class BotStatus:
    INACTIVE = 'inactive'
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'
    SCHEDULED = 'scheduled'

class BotSchedule:
    DAILY = '0 0 * * *'  # Midnight daily
    WEEKLY = '0 0 * * 0'  # Midnight Sunday
    MONTHLY = '0 0 1 * *'  # Midnight 1st of month

class Bot(db.Model):
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
    schedule = db.Column(db.String(100), nullable=True)  # Stores cron expression
    next_run = db.Column(db.DateTime, nullable=True)
    last_error = db.Column(db.Text, nullable=True)
    run_count = db.Column(db.Integer, default=0)
    success_count = db.Column(db.Integer, default=0)
    failure_count = db.Column(db.Integer, default=0)
    average_runtime = db.Column(db.Float, nullable=True)
    last_successful_run = db.Column(db.DateTime, nullable=True)
    consecutive_failures = db.Column(db.Integer, default=0)
    max_runtime = db.Column(db.Float, nullable=True)
    min_runtime = db.Column(db.Float, nullable=True)

    def update_performance_metrics(self, runtime):
        """Update bot performance metrics"""
        if not self.average_runtime:
            self.average_runtime = runtime
        else:
            self.average_runtime = (self.average_runtime + runtime) / 2
            
        if not self.max_runtime or runtime > self.max_runtime:
            self.max_runtime = runtime
            
        if not self.min_runtime or runtime < self.min_runtime:
            self.min_runtime = runtime
            
        if self.status == BotStatus.COMPLETED:
            self.last_successful_run = datetime.utcnow()
            self.consecutive_failures = 0
        else:
            self.consecutive_failures += 1
            
        db.session.commit()

    def __repr__(self):
        return f"<Bot {self.name}>"

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
            'is_active': self.is_active,
            'schedule': self.schedule,
            'next_run': self.next_run.isoformat() if self.next_run else None,
            'run_count': self.run_count,
            'success_count': self.success_count,
            'failure_count': self.failure_count
        }

    def calculate_next_run(self):
        """Calculate next run time based on cron schedule"""
        if not self.schedule:
            return None
            
        now = datetime.utcnow()
        cron = croniter(self.schedule, now)
        return cron.get_next(datetime)
