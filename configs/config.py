"""Consolidated configuration management with validation"""
import logging
import os
import logging.config
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class DatabaseConfig:
    uri: str
    echo: bool = False
    track_modifications: bool = False

class Configuration:
    def __init__(self, env: str = "development"):
        self.env = env
        self.root_path = Path(__file__).parent.parent.resolve()
        
        # Basic configuration
        self.SECRET_KEY: str = os.getenv('SECRET_KEY', 'your-secret-key-here')
        self.DEBUG: bool = False
        self.TESTING: bool = False
        
        # Database configuration
        self.DATABASE: DatabaseConfig = DatabaseConfig(
            uri=os.getenv('DATABASE_URI', 'sqlite:///:memory:'),
            echo=self._get_bool_env('DATABASE_ECHO', 'False'),
            track_modifications=self._get_bool_env('DATABASE_TRACK_MODIFICATIONS', 'False')
        )
        
        # Logging configuration
        self.LOGGING: Dict[str, Any] = {
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

    def _get_bool_env(self, var_name: str, default: str) -> bool:
        """Get boolean environment variable with default"""
        try:
            return os.getenv(var_name, default).lower() == 'true'
        except:
            return False

    def validate(self):
        """Validate configuration settings"""
        # Validate required settings
        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY cannot be empty")
            
        # Validate database URI
        if not self.DATABASE.uri:
            raise ValueError("DATABASE_URI cannot be empty")
            
        # Ensure log file path exists
        log_file = self.LOGGING['handlers']['file']['filename']
        log_dir = os.path.dirname(log_file)
        os.makedirs(log_dir, exist_ok=True)

    def init_app(self, app):
        """Initialize Flask application configuration"""
        app.config.from_object(self)
        
        # Validate configuration
        self.validate()
        
        # Setup logging
        self.configure_logging(app)
        
        # Environment-specific configurations
        if self.env == 'development':
            app.config['DATABASE'].uri = 'sqlite:///dev.db'
            app.config['LOGGING']['root']['level'] = 'DEBUG'
        elif self.env == 'production':
            app.config['DATABASE'].uri = os.getenv('PRODUCTION_DATABASE_URI', 'postgresql://user:pass@host:port/dbname')
            app.config['LOGGING']['root']['level'] = 'INFO'

    def configure_logging(self, app=None):
        """Configure logging for the application"""
        if app is None:
            from flask import current_app
            app = current_app
        logging.config.dictConfig(self.LOGGING)
