from flask import Flask
from app.configs import BaseConfig, DevelopmentConfig, ProductionConfig, TestingConfig
from app.extensions import db, mail, login_manager, migrate, csrf, limiter
from app.routes.admin import register_admin_blueprints

def create_app(config_name='development'):
    app = Flask(__name__)
    
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
    limiter.init_app(app)
    
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
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    from flask_limiter.storage import RedisStorage
    
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        storage=RedisStorage(
            host='localhost',
            port=6379,
            db=0,
            prefix='flask-limiter'
        ),
        default_limits=['200 per minute']
    )
    app.limiter = limiter

    return app
