import logging
import logging.handlers
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
        self.LOGGING_LEVEL: str = 'INFO'
        self.LOG_FILE: str = 'app.log'
        self.MAX_LOG_SIZE: int = 1024 * 1024 * 5  # 5MB
        self.BACKUP_COUNT: int = 3
        
    def configure_logging(self, app=None):
        """Configure logging for the application"""
        if app is not None:
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
            
            # Configure Flask logger
            app.logger = logging.getLogger('flask.app')
            app.logger.setLevel(self.LOGGING_LEVEL)
            app.logger.handlers = [file_handler, console_handler]
            
    def init_app(self, app):
        """Initialize Flask app with this configuration."""
        app.config.from_object(self)
        self._setup_paths(app)
        self.configure_logging(app)
        
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

class DevelopmentConfig(BaseConfig):
    def __init__(self, root_path: Path):
        super().__init__(root_path)
        self.DEBUG = True
        self.SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'

class TestingConfig(BaseConfig):
    def __init__(self, root_path: Path):
        super().__init__(root_path)
        self.TESTING = True
        self.SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
