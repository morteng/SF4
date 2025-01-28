from app.configs.base_config import BaseConfig

class TestingConfig(BaseConfig):
    """Testing environment configuration."""
    
    TESTING: bool = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"
    SQLALCHEMY_ECHO: bool = False
