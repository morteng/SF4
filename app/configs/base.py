import logging
from pathlib import Path
from typing import Dict, Any

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
                }
            },
            'root': {
                'level': 'INFO',
                'handlers': ['console']
            }
        }

    def init_app(self, app):
        """Initialize Flask app with this configuration."""
        app.config.from_object(self)
        self._setup_paths()
        
    def _setup_paths(self):
        """Setup paths used by the application."""
        self.STATIC_FOLDER = self.root_path / 'static'
        self.TEMPLATES_FOLDER = self.root_path / 'templates'
        self.INSTANCE_PATH = self.root_path / 'instance'
        self.LOGS_PATH = self.INSTANCE_PATH / 'logs'
        self.BACKUPS_PATH = self.INSTANCE_PATH / 'backups'
        
        # Ensure directories exist
        self.INSTANCE_PATH.mkdir(exist_ok=True)
        self.LOGS_PATH.mkdir(exist_ok=True)
        self.BACKUPS_PATH.mkdir(exist_ok=True)

class ProductionConfig(BaseConfig):
    def __init__(self, root_path: Path):
        super().__init__(root_path)
        self.DEBUG = False
        self.SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@host:port/dbname'
        self.LOGGING['root']['level'] = 'INFO'

class DevelopmentConfig(BaseConfig):
    def __init__(self, root_path: Path):
        super().__init__(root_path)
        self.DEBUG = True
        self.SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'
        self.LOGGING['root']['level'] = 'DEBUG'

class TestingConfig(BaseConfig):
    def __init__(self, root_path: Path):
        super().__init__(root_path)
        self.TESTING = True
        self.SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
        self.LOGGING['root']['level'] = 'WARNING'
