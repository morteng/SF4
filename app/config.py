from flask_config import Config

class BaseConfig(Config):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSONIFY_PRETTYPRINT_REGULAR = True
    BUNDLE_ERRORS = True
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024  # 25MB

    def init_app(self, app):
        """Base configuration initialization"""
        super().init_app(app)
        app.jinja_env.trim_blocks = True
        app.jinja_env.lstrip_blocks = True

class TestConfig(BaseConfig):
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = 'test-secret-key'
    
    # Configure SQLite for testing
    SQLALCHEMY_ENGINE_OPTIONS = {
        'poolclass': 'StaticPool',
        'connect_args': {'check_same_thread': False}
    }
    
    # Ensure migrations run for in-memory database
    def init_app(self, app):
        super().init_app(app)
        with app.app_context():
            from flask_migrate import upgrade
            upgrade()
            
        # Reset rate limiter storage before each test
        from flask_limiter import Limiter
        limiter = Limiter(app=app)
        limiter.storage.reset()
        
        # Setup test CSRF handling
        @app.before_request
        def set_csrf():
            from flask_wtf.csrf import generate_csrf
            if app.testing:
                # Generate and set CSRF token for all test requests
                csrf_token = generate_csrf()
                from flask import g
                g.csrf_token = csrf_token
