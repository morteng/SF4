import logging
import os
from pathlib import Path
from typing import Dict, Any

class LoggingConfig:
    def __init__(self, root_path: Path):
        self.root_path = root_path
        
    def configure_logging(self, app):
        """Configure logging for the application"""
        self._setup_logging(app)
        
    def _setup_logging(self, app):
        # Define logging configuration
        logging_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'default': {
                    'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': 'DEBUG',
                    'formatter': 'default',
                    'stream': 'ext://sys.stdout'
                },
                'file': {
                    'class': 'logging.FileHandler',
                    'level': 'WARNING',
                    'formatter': 'default',
                    'filename': str(self.root_path / 'instance' / 'logs' / 'app.log'),
                    'mode': 'a',
                    'encoding': 'utf-8'
                }
            },
            'root': {
                'level': 'INFO',
                'handlers': ['console', 'file']
            }
        }
        
        # Apply configuration
        logging.config.dictConfig(logging_config)
        
        # Ensure log directory exists
        log_dir = self.root_path / 'instance' / 'logs'
        log_dir.mkdir(exist_ok=True)
