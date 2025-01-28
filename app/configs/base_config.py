import os
from pathlib import Path
from typing import Dict, Any

class BaseConfig:
    """Base configuration class that other configurations inherit from."""
    
    # Project structure
    PROJECT_NAME: str = "Stipend Discovery Platform"
    PROJECT_ROOT: Path = Path(__file__).parent.parent
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")  # Should be overridden in environment
    SECURITY_PASSWORD_SALT: str = os.getenv("SECURITY_PASSWORD_SALT", "your-salt-here")
    
    # Database
    SQLALCHEMY_DATABASE_URI: str = os.getenv("DATABASE_URL", "sqlite:///:memory:")
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_ECHO: bool = False
    
    # Application features
    TESTING: bool = False
    DEBUG: bool = False
    TRAP_HTTP_EXCEPTIONS: bool = True
    TRAP_BAD_REQUEST_ERRORS: bool = True
    
    # API settings
    OPENAPI_VERSION: str = "3.0.2"
    OPENAPI_URL_PREFIX: str = "/openapi"
    OPENAPI_SWAGGER_UI_PATH: str = "/swagger"
    OPENAPI_SWAGGER_UI_URL: str = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    
    # Rate limiting (if implemented)
    RATE_LIMIT_GLOBAL: str = "100 per minute"
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        # Override any settings from environment variables
        for env_var, default in self._get_env_vars().items():
            setattr(self, env_var, os.getenv(env_var, default))
    
    @classmethod
    def _get_env_vars(cls) -> Dict[str, Any]:
        """Get environment variables and their default values."""
        return {
            "SECRET_KEY": "your-secret-key-here",
            "SECURITY_PASSWORD_SALT": "your-salt-here",
            "DATABASE_URL": "sqlite:///:memory:",
            "DEBUG": "False",
            "TESTING": "False"
        }
