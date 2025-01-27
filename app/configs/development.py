from .base_config import BaseConfig
import os

class DevelopmentConfig(BaseConfig):
    def __init__(self, root_path=None):
        super().__init__(root_path=root_path)
        
        # Override base configuration with development-specific settings
        self.DEBUG = True
        self.SQLALCHEMY_ECHO = True
        self.SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'
        
        # Update logging configuration
        self.LOGGING['handlers']['file']['filename'] = os.path.join(self.LOGS_PATH, 'dev.log')
