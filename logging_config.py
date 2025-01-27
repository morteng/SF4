import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

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
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    logging.getLogger().addHandler(timed_handler)
