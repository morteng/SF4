from pathlib import Path
import logging

class BaseConfig:
    def __init__(self, root_path: Path):
        self.root_path = root_path.resolve()
        
        # Basic configuration
        self.SECRET_KEY: str = 'your-secret-key-here'
        self.DEBUG: bool = False
        self.TESTING: bool = False
        
        # Database configuration
        self.SQLALCHEMY_DATABASE_URI: str = 'sqlite:///:memory:'
        self.SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
        
        # Logging configuration
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
                    'encoding': 'utf-8'
                }
            },
            'root': {
                'level': 'INFO',
                'handlers': ['console', 'file']
            }
        }
        
    def init_app(self, app):
        """Initialize logging for the application."""
        if not app.logger.handlers:
            # Only set up logging if it hasn't been configured yet
            app.logger = logging.getLogger('app')
            logging.config.dictConfig(self.LOGGING)
