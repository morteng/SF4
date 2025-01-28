"""Consolidated configuration management with validation"""
import logging
import os
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    uri: str
    echo: bool = False
    track_modifications: bool = False

@dataclass
class LoggingConfig:
    level: str = 'INFO'
    format: str = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    handlers: Dict[str, Dict[str, Any]] = {
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
            'filename': None,
            'mode': 'a',
            'encoding': 'utf-8'
        }
    }

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
        self.LOGGING: LoggingConfig = LoggingConfig(
            level=os.getenv('LOG_LEVEL', 'INFO'),
            format=os.getenv('LOG_FORMAT', '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'),
            handlers={
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': os.getenv('LOG_LEVEL_CONSOLE', 'DEBUG'),
                    'formatter': 'default',
                    'stream': 'ext://sys.stdout'
                },
                'file': {
                    'class': 'logging.FileHandler',
                    'level': os.getenv('LOG_LEVEL_FILE', 'WARNING'),
                    'formatter': 'default',
                    'filename': self.root_path / 'app.log',
                    'mode': 'a',
                    'encoding': 'utf-8'
                }
            }
        )

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
        log_file = self.LOGGING.handlers['file']['filename']
        if log_file:
            log_dir = os.path.dirname(log_file)
            os.makedirs(log_dir, exist_ok=True)

    def init_app(self, app):
        """Initialize Flask application configuration"""
        app.config.from_object(self)
        
        # Validate configuration
        self.validate()
        
        # Setup logging
        self._configure_logging(app)
        
        # Environment-specific configurations
        if self.env == 'development':
            app.config['DATABASE'].uri = 'sqlite:///dev.db'
            app.config['LOGGING'].level = 'DEBUG'
        elif self.env == 'production':
            app.config['DATABASE'].uri = os.getenv('PRODUCTION_DATABASE_URI', 'postgresql://user:pass@host:port/dbname')
            app.config['LOGGING'].level = 'INFO'

    def _configure_logging(self, app):
        """Configure logging for the application"""
        # Remove existing handlers
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Apply configuration
        logging.config.dictConfig({
            'version': 1,
            'formatters': {
                'default': {
                    'format': self.LOGGING.format,
                }
            },
            'handlers': {
                'console': self.LOGGING.handlers['console'],
                'file': {
                    **self.LOGGING.handlers['file'],
                    'filename': str(self.LOGGING.handlers['file']['filename'])
                }
            },
            'root': {
                'level': self.LOGGING.level,
                'handlers': ['console', 'file']
            }
        })
