from flask import Flask
from app.extensions import db, login_manager

def create_app(config_name='development'):
    app = Flask(__name__)

    if config_name == 'testing':
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SERVER_NAME'] = 'localhost'
        app.config['APPLICATION_ROOT'] = '/'
        app.config['PREFERRED_URL_SCHEME'] = 'http'
    else:
        app.config.from_object(f'app.config.{config_name}_config')

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    from app.routes.admin import register_admin_blueprints
    register_admin_blueprints(app)

    return app

def register_blueprints(app):
    pass  # This function can be used to register other blueprints if needed
