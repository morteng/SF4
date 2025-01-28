"""Consolidated configuration and logging management"""
import logging
import os
from pathlib import Path
from typing import Dict, Any

class Configuration:
    def __init__(self, env: str = "development"):
        self.env = env
        self.root_path = Path(__file__).parent.parent.resolve()
        
        # Basic configuration
        self.SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
        self.DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "on", "1")
        self.TESTING: bool = os.getenv("TESTING", "False").lower() in ("true", "on", "1")
        
        # Database configuration
        self.SQLALCHEMY_DATABASE_URI: str = os.getenv("DATABASE_URL", "sqlite:///:memory:")
        self.SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
        self.SQLALCHEMY_ECHO: bool = False
        
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
                    'filename': str(self.root_path / 'instance' / 'app.log'),
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
        
        # Setup paths
        self._setup_paths(app)
        
        # Environment-specific configurations
        if self.env == 'development':
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dev.db'
            app.config['LOGGING']['root']['level'] = 'DEBUG'
        elif self.env == 'production':
            app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "postgresql://user:pass@host:port/dbname")
            app.config['LOGGING']['root']['level'] = 'INFO'

    def _setup_paths(self, app):
        """Setup paths used by the application"""
        # Ensure directories exist
        (self.root_path / 'instance').mkdir(exist_ok=True)
        (self.root_path / 'instance' / 'logs').mkdir(exist_ok=True)
        (self.root_path / 'instance' / 'backups').mkdir(exist_ok=True)

        # Set Flask-specific paths
        app.static_folder = str(self.root_path / 'static')
        app.template_folder = str(self.root_path / 'templates')

    def __getitem__(self, key):
        return getattr(self, key, None)

    def get(self, key, default=None):
        return getattr(self, key, default)
