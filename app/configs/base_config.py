import os
from pathlib import Path

class BaseConfig:
    PROJECT_NAME = "Stipend Discovery Platform"
    PROJECT_ROOT = Path(__file__).parent.parent
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///:memory:")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    TESTING = False
    DEBUG = False
