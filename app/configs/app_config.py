from .base_config import BaseConfig

class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///production.db'
    DEBUG = False
