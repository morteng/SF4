import os
import logging
from pathlib import Path
from typing import Dict, Any

class BaseConfig:
    """Base configuration class that other configurations inherit from."""
    
    # Project structure
    PROJECT_NAME: str = "Stipend Discovery Platform"
    PROJECT_ROOT: Path = Path(__file__).parent.parent
    LOGS_PATH: Path = PROJECT_ROOT / 'logs'
    STATIC_FOLDER: Path = PROJECT_ROOT / 'static'
    TEMPLATES_FOLDER: Path = PROJECT_ROOT / 'templates'
    INSTANCE_PATH: Path = PROJECT_ROOT / 'instance'
    BACKUPS_PATH: Path = INSTANCE_PATH / 'backups'
    
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
        
    def init_app(self, app):
        """Initialize Flask app with this configuration."""
        app.config.from_object(self)
        self._setup_paths(app)
        
    def _setup_paths(self, app):
        """Setup paths used by the application."""
        # Ensure directories exist
        self.INSTANCE_PATH.mkdir(exist_ok=True)
        self.LOGS_PATH.mkdir(exist_ok=True)
        self.BACKUPS_PATH.mkdir(exist_ok=True)
        
        # Set Flask-specific paths
        app.static_folder = str(self.STATIC_FOLDER)
        app.template_folder = str(self.TEMPLATES_FOLDER)
    
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

class ProductionConfig(BaseConfig):
    def __init__(self):
        super().__init__()
        self.DEBUG = False
        self.SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://user:password@host:port/dbname")

class DevelopmentConfig(BaseConfig):
    def __init__(self):
        super().__init__()
        self.DEBUG = True
        self.SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'

class TestingConfig(BaseConfig):
    def __init__(self):
        super().__init__()
        self.TESTING = True
        self.SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
