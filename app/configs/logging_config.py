import logging
from pathlib import Path
import os

class LoggingConfig:
    def __init__(self, root_path: Path):
        self.root_path = root_path.resolve()
        
        self.LOGGING = {
            'version': 1,
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
                    'filename': self.root_path / 'app.log',
                    'mode': 'a',
                    'encoding': 'utf-8',
                    'delay': False
                }
            },
            'root': {
                'level': 'DEBUG',
                'handlers': ['console', 'file']
            }
        }

    def init_app(self, app):
        """Initialize logging for the application."""
        if not app.logger.handlers:
            # Only set up logging if it hasn't been configured yet
            app.logger = logging.getLogger('app')
            logging.config.dictConfig(self.LOGGING)
