from .base_config import BaseConfig

class TestingConfig(BaseConfig):
    __test__ = False  # Explicitly disable pytest test collection
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_ECHO = True
    TESTING = True
    WTF_CSRF_ENABLED = False  # Disabled only for testing
