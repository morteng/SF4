import logging
import os
import json
from pathlib import Path
from functools import wraps
from flask import flash, redirect, url_for, abort, request, current_app
from flask_login import current_user
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from app.models.audit_log import AuditLog
from app.models.notification import Notification
from app.models.user import User
from app.extensions import db
from app.constants import FlashMessages, FlashCategory
from contextlib import contextmanager

def configure_logging(app):
    """Centralized logging configuration"""
    # Set default log path if not provided
    app.config.setdefault('LOG_PATH', str(Path(app.root_path).joinpath('instance', 'logs', 'app.log')))
    
    # Create directory if it doesn't exist
    log_dir = os.path.dirname(app.config['LOG_PATH'])
    os.makedirs(log_dir, exist_ok=True)

    # Clear existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Base configuration
    logging.basicConfig(
        level=os.getenv('LOG_LEVEL', 'INFO'),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(app.config['LOG_PATH']),
            logging.StreamHandler()
        ]
    )

    # Configure file handlers
    _configure_file_handlers(app)

def _configure_file_handlers(app):
    """Configure additional file handlers for logging"""
    # Add rotating file handler
    rotating_handler = RotatingFileHandler(
        app.config['LOG_PATH'],
        maxBytes=1024*1024*10,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    rotating_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    logging.getLogger().addHandler(rotating_handler)

    # Add timed rotating file handler for hourly logs
    timed_handler = TimedRotatingFileHandler(
        app.config['LOG_PATH'],
        when='H',  # Hourly
        interval=24,  # Keep 24 hours worth of logs
        backupCount=24,
        encoding='utf-8'
    )
    timed_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    ))
    logging.getLogger().addHandler(timed_handler)

def remove_logging_handlers():
    """Remove all existing logging handlers"""
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name"""
    logger = logging.getLogger(name)
    logger.setLevel(os.getenv('LOG_LEVEL', 'INFO'))
    return logger

def admin_required(f):
    """Decorator requiring admin privileges."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash_message(FlashMessages.LOGIN_REQUIRED.value, FlashCategory.ERROR.value)
            return redirect(url_for('public.login'))

        if not current_user.is_admin:
            _log_unauthorized_admin_access()
            flash_message(FlashMessages.ADMIN_ACCESS_DENIED.value, FlashCategory.ERROR.value)
            return abort(403)

        # Create audit log for valid admin access
        _log_admin_access(f)
        return f(*args, **kwargs)

    return decorated_function

def _log_unauthorized_admin_access():
    """Log unauthorized admin access attempts."""
    try:
        audit_log = AuditLog(
            user_id=current_user.id if current_user.is_authenticated else None,
            action='unauthorized_access',
            object_type='AdminPanel',
            details=f'Attempted access to {request.path}',
            ip_address=request.remote_addr,
            http_method=request.method,
            endpoint=request.endpoint
        )
        db.session.add(audit_log)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Error creating audit log: {str(e)}")
        db.session.rollback()

    try:
        notification = Notification(
            type='security',
            message=f'Unauthorized access attempt to {request.path}',
            user_id=current_user.id
        )
        db.session.add(notification)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Error creating notification: {str(e)}")
        db.session.rollback()

def _log_admin_access(f):
    """Log authorized admin route access."""
    try:
        audit_log = AuditLog(
            user_id=current_user.id,
            action=f.__name__,
            details=f"Accessed admin route: {request.path}",
            ip_address=request.remote_addr,
            http_method=request.method,
            endpoint=request.endpoint
        )
        db.session.add(audit_log)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Error creating audit log: {str(e)}")
        db.session.rollback()

def log_audit(user_id, action, object_type=None, object_id=None, before=None, after=None):
    """Create an audit log entry with enhanced error handling and logging."""
    try:
        if not db.engine.has_table('audit_log'):
            logger.error("audit_log table does not exist")
            raise RuntimeError("audit_log table not found")

        # Validate required fields
        if not user_id:
            logger.error("Missing user_id in audit log")
            raise ValueError("user_id is required")
        if not action:
            logger.error("Missing action in audit log")
            raise ValueError("action is required")

        # Validate object_type / object_id consistency
        if object_type and not object_id:
            raise ValueError("object_id is required when object_type is provided")
        if object_id and not object_type:
            raise ValueError("object_type is required when object_id is provided")

        if len(action) > 100:
            raise ValueError("Action exceeds maximum length of 100 characters")
        if object_type and len(object_type) > 50:
            raise ValueError("Object type exceeds maximum length of 50 characters")

        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            object_type=object_type,
            object_id=object_id,
            details_before=json.dumps(before) if before else None,
            details_after=json.dumps(after) if after else None,
            ip_address=request.remote_addr if request else '0.0.0.0',
            http_method=request.method if request else 'UNKNOWN',
            endpoint=request.endpoint if request else 'unknown'
        )
        with db_session_scope() as session:
            session.add(audit_log)
            session.commit()

        logger.info(f"Audit log created: {action} by user {user_id}")
        return audit_log

    except Exception as e:
        logger.error(f"Failed to create audit log: {str(e)}", exc_info=True)
        db.session.rollback()
        raise

def create_notification(type, message, related_object=None, user_id=None):
    """Create a notification."""
    try:
        notification = Notification(
            type=type,
            message=message,
            related_object=related_object,
            user_id=user_id
        )
        db.session.add(notification)
        db.session.commit()
    except Exception as e:
        logger.error(f"Failed to create notification: {e}")
        db.session.rollback()

def flash_message(message, category):
    """Flash a message and log it if necessary."""
    try:
        flash(message, category)
        if category == FlashCategory.ERROR:
            logger.error(f"Flash Error: {message}")
        elif category == FlashCategory.WARNING:
            logger.warning(f"Flash Warning: {message}")
    except Exception as e:
        logger.error(f"Failed to flash message: {e}")

def clean(text, tags=None, attributes=None):
    """Sanitize input text using bleach."""
    if not text:
        return text
    from bleach import clean as bleach_clean
    return bleach_clean(text, tags=tags, attributes=attributes)

@contextmanager
def db_session_scope():
    """Provide a transactional scope for DB operations."""
    session = db.session
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database operation failed: {str(e)}")
        raise
    finally:
        session.close()

logger = logging.getLogger(__name__)
