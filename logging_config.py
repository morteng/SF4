import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

def configure_logging(app):
    """Centralized logging configuration"""
    # Set default log path if not provided
    app.config.setdefault('LOG_PATH', 'instance/logs/app.log')
    
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
