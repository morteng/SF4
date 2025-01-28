from app.configs.base_config import BaseConfig

class ProductionConfig(BaseConfig):
    """Production environment configuration."""
    
    DEBUG: bool = False
    TESTING: bool = False
    SQLALCHEMY_DATABASE_URI: str = os.getenv("DATABASE_URL", "postgresql://user:password@host:port/dbname")
    SECRET_KEY: str = os.getenv("SECRET_KEY", None)  # Should be set in environment variables
