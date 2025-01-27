from flask import Flask
from app.models import db
from flask_wtf.csrf import CSRFError
from app.routes import register_blueprints
from app.routes.admin import register_admin_blueprints

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    app.debug = app.config.get('DEBUG', False)

    # Initialize extensions
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
