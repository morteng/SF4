from .default import DefaultConfig

class ProductionConfig(DefaultConfig):
    DEBUG = False
    TESTING = False
