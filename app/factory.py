from flask import Flask
from app.configs import BaseConfig, DevelopmentConfig, ProductionConfig, TestingConfig
from app.extensions import db, mail
from app.blueprints import admin_bp
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from flask import jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_wtf.csrf import CSRFProtect
import logging

def create_app(config_name='development'):
    app = Flask(__name__)
    
    if config_name == 'development':
        app.config.from_object(DevelopmentConfig())
    elif config_name == 'production':
        app.config.from_object(ProductionConfig(app.root_path))
    elif config_name == 'testing':
        app.config.from_object(TestingConfig(app.root_path))
    else:
        raise ValueError(f'Invalid config name: {config_name}')

    # Initialize extensions
    db.init_app(app)
    mail.init_app(app)
    Talisman(app)
    CORS(app)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)
    csrf = CSRFProtect(app)
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=['200 per minute']
    )
    app.limiter = limiter
    
    # Register blueprints
    app.register_blueprint(admin_bp)
    
    # Error handlers
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return jsonify({'error': 'CSRF token missing or invalid'}), 400

    @app.errorhandler(403)
    def forbidden_page(e):
        return jsonify({'error': 'Forbidden'}), 403
        
    @app.errorhandler(404)
    def page_not_found(e):
        return jsonify({'error': 'Page not found'}), 404
            
    return app

class Factory:
    def create_app(self, config_name='development'):
        return create_app(config_name)
