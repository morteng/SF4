from .base_config import BaseConfig
import os

class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///prod.db'
    # Override base logging configuration
    LOGGING = {
        'version': 1,
        'formatters': {
            'default': {
                'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
            }
        },
        'handlers': {
            'file': {
                'class': 'RotatingFileHandler',
                'level': 'INFO',
                'formatter': 'default',
                'filename': os.path.join(self.LOGS_PATH, 'prod.log'),
                'mode': 'a',
                'maxBytes': 1048576,
                'backupCount': 3
            }
        },
        'root': {
            'level': 'INFO',
            'handlers': ['file']
        }
    }
