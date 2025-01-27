class TestConfig(Config):
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
    @classmethod
    def init_app(cls, app):
        super().init_app(app)
        with app.app_context():
            from flask_migrate import upgrade
            upgrade()
    
    # CSRF testing configuration
    WTF_CSRF_CHECK_DEFAULT = True
    WTF_CSRF_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour for tests
    WTF_CSRF_SSL_STRICT = False  # Disable SSL strict for testing
    SERVER_NAME = 'localhost'
    APPLICATION_ROOT = '/'
    PREFERRED_URL_SCHEME = 'http'
    
    # Disable all rate limiting in tests
    RATELIMIT_ENABLED = False
    RATELIMIT_STORAGE = 'redis://localhost:6379/0'
    RATELIMIT_DEFAULT = "9999999 per second"
    RATELIMIT_USER_MANAGEMENT = "9999999 per second"
    RATELIMIT_BOT_OPERATIONS = "9999999 per second"
    RATELIMIT_LOGIN = "9999999 per second"
    RATELIMIT_GLOBAL = "9999999 per second"
    RATELIMIT_HEADERS_ENABLED = False
    RATELIMIT_IN_MEMORY_FALLBACK_ENABLED = True
    RATELIMIT_STRATEGY = 'fixed-window-elastic-expiry'
    
    # Logging configuration
    LOGGING_CONFIG = {
        'version': 1,
        'formatters': {
            'standard': {
                'format': '%(asctime)s - %(levelname)s - %(message)s'
            },
        },
        'handlers': {
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'logs/app.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'formatter': 'standard'
            },
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'standard'
            }
        },
        'root': {
            'level': 'INFO',
            'handlers': ['file', 'console']
        }
    }
    
    # Notification settings
    NOTIFICATION_MAX_COUNT = 1000  # Increase for testing
    NOTIFICATION_CLEANUP_INTERVAL = 0  # Disable cleanup during tests

    @classmethod
    def init_app(cls, app):
        """Initialize the test application"""
        super().init_app(app)
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
