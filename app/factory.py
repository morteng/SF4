import os
from flask import Flask
from flask_wtf.csrf import CSRFError
from app.routes import register_blueprints
from app.routes.admin import admin_bp
from app.extensions import db, login_manager, migrate, csrf, limiter, init_extensions

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY') or os.urandom(24)
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///stipend.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///stipend.db'

class TestingConfig(Config):
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = True

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///stipend.db'

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    app.debug = app.config.get('DEBUG', False)

    # Initialize extensions
    init_extensions(app)
    
    # Register blueprints
    register_blueprints(app)
    app.register_blueprint(admin_bp)
    
    # Error handlers
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return {'error': 'CSRF token missing or invalid'}, 400

    return app

config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
