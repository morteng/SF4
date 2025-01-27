import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

def configure_logging(app):
    """Centralized logging configuration"""
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
    """Configure rotating and timed file handlers"""
    log_dir = Path(app.config['LOG_PATH']).parent
    log_dir.mkdir(exist_ok=True)

    # Application logs
    app_handler = RotatingFileHandler(
        app.config['LOG_PATH'],
        maxBytes=1024*1024*5,  # 5MB
        backupCount=5,
        encoding='utf-8'
    )
    app_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logging.getLogger().addHandler(app_handler)

    # Audit logs
    audit_handler = TimedRotatingFileHandler(
        log_dir / 'audit.log',
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    audit_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    audit_logger = logging.getLogger('audit')
    audit_logger.handlers = [audit_handler]
    audit_logger.setLevel(os.getenv('AUDIT_LOG_LEVEL', 'INFO'))

    # Error logs
    error_handler = RotatingFileHandler(
        log_dir / 'error.log',
        maxBytes=1024*1024*5,
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    error_logger = logging.getLogger('error')
    error_logger.handlers = [error_handler]
    error_logger.setLevel(os.getenv('ERROR_LOG_LEVEL', 'ERROR'))
