import os
import logging
from flask import Config

class BaseConfig(Config):
    # Directory structure
    ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    LOGS_PATH = os.path.join(ROOT_PATH, 'logs')
    UPLOAD_FOLDER = os.path.join(ROOT_PATH, 'uploads')
    DOWNLOAD_FOLDER = os.path.join(ROOT_PATH, 'downloads')
    
    def __init__(self, root_path=None):
        if root_path:
            self.ROOT_PATH = root_path
            self.LOGS_PATH = os.path.join(root_path, 'logs')
            self.UPLOAD_FOLDER = os.path.join(root_path, 'uploads')
            self.DOWNLOAD_FOLDER = os.path.join(root_path, 'downloads')
        super().__init__(root_path=root_path)
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
        self.SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///:memory:')
        self.JSONIFY_PRETTYPRINT_REGULAR = True
        self.BUNDLE_ERRORS = True
        self.MAX_CONTENT_LENGTH = 25 * 1024 * 1024  # 25MB
        
        # Mail Configuration
        self.MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
        self.MAIL_PORT = int(os.getenv('MAIL_PORT', 465))
        self.MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'false').lower() in ('true', 'on', '1')
        self.MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'true').lower() in ('true', 'on', '1')
        self.MAIL_USERNAME = os.getenv('MAIL_USERNAME')
        self.MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
        
        # Logging Configuration
        self.LOGGING = {
            'version': 1,
            'formatters': {
                'default': {
                    'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': 'INFO',
                    'formatter': 'default'
                },
                'file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'level': 'DEBUG',
                    'formatter': 'default',
                    'filename': os.path.join(self.LOGS_PATH, 'app.log'),
                    'mode': 'a',
                    'maxBytes': 1048576,
                    'backupCount': 3
                }
            },
            'root': {
                'level': 'DEBUG',
                'handlers': ['console', 'file']
            }
        }
        
        # Flask-Limiter Configuration
        self.RATE_LIMIT_GLOBAL = "200 per minute"
        self.RATE_LIMITS = {
            "create": "50 per minute",
            "update": "50 per minute",
            "delete": "20 per minute"
        }
        
        # Security
        self.SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24))
        self.CSRF_ENABLED = True
        self.CSRF_SECRET = os.getenv('CSRF_SECRET', os.urandom(24))
        
        # Create directories if they don't exist
        if self.ROOT_PATH:
            for path in [self.LOGS_PATH, self.UPLOAD_FOLDER, self.DOWNLOAD_FOLDER]:
                if not os.path.exists(path):
                    os.makedirs(path)
