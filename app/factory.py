from flask import Flask
from app.configs import BaseConfig, DevelopmentConfig, ProductionConfig, TestingConfig
from app.extensions import db, mail, login_manager, migrate, csrf
from app.routes.admin import register_admin_blueprints
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

def create_app(config_name='development'):
    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    app = Flask(__name__, root_path=root_path)
    
    if config_name == 'development':
        app.config.from_object(DevelopmentConfig())
    elif config_name == 'production':
        app.config.from_object(ProductionConfig())
    elif config_name == 'testing':
        app.config.from_object(TestingConfig())
    else:
        raise ValueError(f'Invalid config name: {config_name}')
    
    # Initialize extensions
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    # Register blueprints
    register_admin_blueprints(app)
    
    # Error handlers
    @app.errorhandler(403)
    def forbidden_page(e):
        return {'error': 'Forbidden'}, 403

    @app.errorhandler(404)
    def page_not_found(e):
        return {'error': 'Page not found'}, 404

    # Initialize logging
    if app.config.get('LOGGING'):
        import logging.config
        logging.config.dictConfig(app.config['LOGGING'])
    
    # Initialize Flask-Limiter with Redis storage
    limiter = Limiter(
        key_func=get_remote_address,
        storage_uri=app.config['REDIS_URL']
    )
    limiter.init_app(app)
    app.limiter = limiter

    return app
