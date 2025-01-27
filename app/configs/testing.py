from .base_config import BaseConfig

class TestConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_ECHO = True
    TESTING = True
