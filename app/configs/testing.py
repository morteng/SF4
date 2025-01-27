from .base_config import BaseConfig
import os

class TestingConfig(BaseConfig):
    __test__ = False  # Explicitly disable pytest test collection
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_ECHO = True
    TESTING = True
    WTF_CSRF_ENABLED = False  # Disabled only for testing
    # Override base logging configuration
    LOGGING = {
        'version': 1,
        'formatters': {
            'default': {
                'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
            }
        },
        'handlers': {
            'test_console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'formatter': 'default'
            }
        },
        'root': {
            'level': 'DEBUG',
            'handlers': ['test_console']
        }
    }
