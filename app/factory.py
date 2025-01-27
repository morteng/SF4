import os
from flask import Flask
from flask_wtf.csrf import CSRFError
from app.routes import register_blueprints
from app.routes.admin import admin_bp
from app.extensions import db, login_manager, migrate, csrf, limiter, init_extensions
from app.configs import DevelopmentConfig, ProductionConfig, TestingConfig

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
    init_extensions(app)
    
    # Register blueprints
    register_blueprints(app)
    app.register_blueprint(admin_bp)
    
    # Error handlers
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return {'error': 'CSRF token missing or invalid'}, 400

    @app.errorhandler(403)
    def forbidden_page(e):
        return {'error': 'Forbidden'}, 403
        
    @app.errorhandler(404)
    def page_not_found(e):
        return {'error': 'Page not found'}, 404
            
    return app

class Factory:
    def create_app(self, config_name='development'):
        return create_app(config_name)
