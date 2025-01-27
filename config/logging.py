import logging
import sys
from logging.handlers import RotatingFileHandler

def configure_logging(app):
    # Set up logging format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Set up file handler
    file_handler = RotatingFileHandler(
        'stipend_discovery.log',
        maxBytes=1024*1024*100,  # 100MB
        backupCount=20,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    
    # Set up console handler for non-production environments
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Add handlers
    root_logger.addHandler(file_handler)
    if not app.config['ENV'] == 'production':
        root_logger.addHandler(console_handler)
        
    # Remove any existing handlers to prevent duplication
    while len(root_logger.handlers) > 2:
        root_logger.removeHandler(root_logger.handlers[0])
