from .base_config import BaseConfig
import os

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'
    # Override base logging configuration
    LOGGING = {
        'version': 1,
        'formatters': {
            'default': {
                'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'formatter': 'default'
            },
            'file': {
                'class': 'RotatingFileHandler',
                'level': 'DEBUG',
                'formatter': 'default',
                'filename': os.path.join(BaseConfig.LOGS_PATH, 'dev.log'),
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
