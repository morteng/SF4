import os
from typing import Dict, Any

class Configuration:
    def __init__(self, env: str = "development"):
        self.env = env
        self.load_configurations()
        
    def load_configurations(self) -> None:
        # General configurations
        self.DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "on", "1")
        self.SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
        self.PORT = int(os.getenv("PORT", "5000"))
        
        # Database configurations
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database.db")
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
        self.SQLALCHEMY_ECHO = False
        
        # Logging configurations
        self.LOGGING = {
            "version": 1,
            "formatters": {
                "default": {
                    "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                    "formatter": "default"
                },
                "file": {
                    "class": "logging.FileHandler",
                    "filename": "app.log",
                    "formatter": "default"
                }
            },
            "root": {
                "level": "INFO",
                "handlers": ["console", "file"]
            }
        }
        
    def get_config(self) -> Dict[str, Any]:
        return {
            "DEBUG": self.DEBUG,
            "SECRET_KEY": self.SECRET_KEY,
            "PORT": self.PORT,
            "SQLALCHEMY_DATABASE_URI": self.DATABASE_URL,
            "SQLALCHEMY_TRACK_MODIFICATIONS": self.SQLALCHEMY_TRACK_MODIFICATIONS,
            "SQLALCHEMY_ECHO": self.SQLALCHEMY_ECHO,
            "LOGGING": self.LOGGING
        }
