from pathlib import Path
import logging

class BaseConfig:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path).resolve()
        
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
                    'class': 'logging.handlers.RotatingFileHandler',
                    'level': 'WARNING',
                    'formatter': 'default',
                    'filename': 'app.log',
                    'mode': 'a',
                    'maxBytes': 104857600,  # 100MB
                    'backupCount': 20,
                    'encoding': 'utf-8',
                    'delay': False
                }
            },
            'root': {
                'level': 'DEBUG',
                'handlers': ['console', 'file']
            }
        }
        
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
    def __init__(self, root_path: str):
        super().__init__(root_path)
        self.DEBUG = False
        self.SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@host:port/dbname'

class DevelopmentConfig(BaseConfig):
    def __init__(self, root_path: str):
        super().__init__(root_path)
        self.DEBUG = True
        self.SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'

class TestingConfig(BaseConfig):
    def __init__(self, root_path: str):
        super().__init__(root_path)
        self.TESTING = True
        self.SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
