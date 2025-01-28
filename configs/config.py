"""Consolidated configuration and logging management"""
import logging
from pathlib import Path
from typing import Dict, Any

class Configuration:
    def __init__(self, env: str = "development"):
        self.env = env
        self.root_path = Path(__file__).parent.parent.resolve()
        
        # Basic configuration
        self.SECRET_KEY: str = 'your-secret-key-here'
        self.DEBUG: bool = False
        self.TESTING: bool = False
        
        # Database configuration
        self.SQLALCHEMY_DATABASE_URI: str = 'sqlite:///:memory:'
        self.SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
        
        # Logging configuration
        self.LOGGING: Dict[str, Any] = {
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
        """Initialize Flask application configuration"""
        app.config.from_object(self)
        
        # Setup logging
        self._configure_logging(app)
        
        # Environment-specific configurations
        if self.env == 'development':
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dev.db'
            app.config['LOGGING']['root']['level'] = 'DEBUG'
        elif self.env == 'production':
            app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:pass@host:port/dbname'
            app.config['LOGGING']['root']['level'] = 'INFO'

    def _configure_logging(self, app):
        """Configure logging for the application"""
        # Remove existing handlers
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Apply configuration
        logging.config.dictConfig(app.config['LOGGING'])
