from flask import Flask
from app.configs import BaseConfig, ProductionConfig, TestingConfig
from app.extensions import db, mail, login_manager, migrate, csrf
from app.routes.admin import register_admin_blueprints
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from logging_config import configure_logging

def create_app(config_name='development'):
    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    app = Flask(__name__, root_path=root_path)
    
    # Ensure instance directory exists
    instance_path = app.instance_path
    if instance_path:
        os.makedirs(instance_path, exist_ok=True)
    
    # Select the appropriate config
    config = {
        'development': BaseConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    app_config = config[config_name](root_path=root_path)
    app.config.from_object(app_config)
    
    # Initialize logging
    configure_logging(app)
    
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

    # Initialize Flask-Limiter with Redis storage
    limiter = Limiter(
        key_func=get_remote_address,
        storage_uri=app.config['REDIS_URL']
    )
    limiter.init_app(app)
    app.limiter = limiter

    return app
