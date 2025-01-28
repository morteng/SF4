from app.configs.base_config import BaseConfig

class DevelopmentConfig(BaseConfig):
    """Development environment configuration."""
    
    DEBUG: bool = True
    TESTING: bool = True
    SQLALCHEMY_ECHO: bool = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///dev.db"
