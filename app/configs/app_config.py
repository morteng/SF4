from flask import Config

class BaseConfig(Config):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSONIFY_PRETTYPRINT_REGULAR = True
    BUNDLE_ERRORS = True
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024  # 25MB
    ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    def init_app(self, app):
        """Base configuration initialization"""
        super().init_app(app)
        app.jinja_env.trim_blocks = True
        app.jinja_env.lstrip_blocks = True
        app.root_path = self.ROOT_PATH
        
        # Logging configuration
        log_dir = Path(self.ROOT_PATH) / 'logs'
        log_dir.mkdir(exist_ok=True)
        app.config['LOG_PATH'] = str(log_dir / 'app.log')
        
        from .logging_config import configure_logging
        configure_logging(app)

class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///production.db'
    DEBUG = False

    def init_app(self, app):
        super().init_app(app)
        # Add production-specific configurations
        app.config.from_object('app.configs.ProductionConfig')
