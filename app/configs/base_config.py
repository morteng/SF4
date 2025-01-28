from pathlib import Path

class BaseConfig:
    def __init__(self, root_path: Path):
        self.root_path = root_path.resolve()
        
        # Basic configuration
        self.SECRET_KEY: str = 'your-secret-key-here'
        self.DEBUG: bool = False
        self.TESTING: bool = False
        
        # Database configuration
        self.SQLALCHEMY_DATABASE_URI: str = 'sqlite:///:memory:'
        self.SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    def init_app(self, app):
        """Initialize the base configuration."""
        app.config.from_object(self)
