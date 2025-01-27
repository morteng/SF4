from flask import Flask
from flask_wtf.csrf import CSRFError
from app.routes import register_blueprints
from app.routes.admin import register_admin_blueprints
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import SQLAlchemy
import os

# Initialize SQLAlchemy
db = None

def init_db():
    global db
    db = SQLAlchemy()
    return db

# Create a configured "Session" class
engine = create_engine('sqlite:///stipend.db')
Session = sessionmaker(bind=engine)
db_session = Session()
Base = declarative_base()

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
    db = init_db()
    db.init_app(app)
    
    # Register blueprints
    register_blueprints(app)
    register_admin_blueprints(app)
    
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
