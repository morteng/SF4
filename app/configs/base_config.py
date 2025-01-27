from flask import Config
from flask_mail import Mail
import os
import logging
from logging.handlers import RotatingFileHandler

class BaseConfig(Config):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///:memory:')
    JSONIFY_PRETTYPRINT_REGULAR = True
    BUNDLE_ERRORS = True
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024  # 25MB
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 465))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'false').lower() in ('true', 'on', '1')
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'true').lower() in ('true', 'on', '1')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    
    def __init__(self):
        super().__init__()
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
                    'level': 'ERROR',
                    'formatter': 'default',
                    'stream': 'ext://sys.stdout'
                },
                'file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'level': 'INFO',
                    'formatter': 'default',
                    'filename': os.path.join(self.root_path, 'instance', 'app.log'),
                    'maxBytes': 1024*1024*100,  # 100MB
                    'backupCount': 20,
                    'encoding': 'utf-8'
                }
            },
            'root': {
                'level': 'INFO',
                'handlers': ['console', 'file']
            }
        }
    
    def init_app(self, app):
        """Base configuration initialization"""
        app.config.from_object(self)
        app.jinja_env.trim_blocks = True
        app.jinja_env.lstrip_blocks = True
        
        # Initialize Flask-Limiter with proper storage
        from flask_limiter import Limiter
        from flask_limiter.util import get_remote_address
        from flask_limiter.storage import RedisStorage
        
        limiter = Limiter(
            app=app,
            key_func=get_remote_address,
            storage=RedisStorage(
                host='localhost',
                port=6379,
                db=0,
                prefix='flask-limiter'
            ),
            default_limits=['200 per minute']
        )
        app.limiter = limiter
        
        # Initialize logging
        import logging.config
        logging.config.dictConfig(app.config['LOGGING'])
