import logging
import os
from pathlib import Path
import logging.handlers
from typing import Dict, Any

class LoggingConfig:
    def __init__(self, root_path: Path):
        self.root_path = root_path.resolve()
        
        # Configure logging parameters
        self.LOGGING_LEVEL: str = os.getenv('LOGGING_LEVEL', 'INFO')
        self.LOG_FILE: str = 'app.log'
        self.MAX_LOG_SIZE: int = 1024 * 1024 * 5  # 5MB
        self.BACKUP_COUNT: int = 3
        
    def configure_logging(self, app=None):
        """Configure logging for the application"""
        self._setup_logging(app)
        
    def _setup_logging(self, app):
        # Remove existing handlers
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
            
        # Configure formatters
        default_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        # Setup file handler
        log_dir = self.root_path / 'instance' / 'logs'
        log_dir.mkdir(exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_dir / self.LOG_FILE,
            maxBytes=self.MAX_LOG_SIZE,
            backupCount=self.BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setFormatter(logging.Formatter(default_format))
        
        # Setup console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(default_format))
        
        # Add handlers to root logger
        logging.root.setLevel(self.LOGGING_LEVEL)
        logging.root.addHandler(file_handler)
        logging.root.addHandler(console_handler)
        
        # Configure Flask logger if app is available
        if app:
            app.logger = logging.getLogger('flask.app')
            app.logger.setLevel(self.LOGGING_LEVEL)
            app.logger.handlers = [file_handler, console_handler]
