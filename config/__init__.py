from .default import DefaultConfig
from .development import DevelopmentConfig
from .testing import TestingConfig
from .production import ProductionConfig

def get_config(config_name):
    config_map = {
        'default': DefaultConfig,
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': ProductionConfig
    }
    return config_map.get(config_name, DefaultConfig)
