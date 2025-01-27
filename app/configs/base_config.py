from flask import Config
import os
from flask_mail import Mail
import logging
from .logging import LOGGING

class BaseConfig(Config):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///:memory:')
    JSONIFY_PRETTYPRINT_REGULAR = True
    BUNDLE_ERRORS = True
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024  # 25MB
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 465))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'false').lower() in ('true', 'on', '1')
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'true').lower() in ('true', 'on', '1')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    
    # Logging configuration
    LOGGING = LOGGING
    
    # Flask-Limiter configuration
    RATE_LIMIT_GLOBAL = "200 per minute"
    RATE_LIMITS = {
        "create": "50 per minute",
        "update": "50 per minute",
        "delete": "20 per minute"
    }
