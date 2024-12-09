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
        from app.config import config_by_name
        app.config.from_object(config_by_name[config_name])

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    from app.routes.admin import register_admin_blueprints
    register_admin_blueprints(app)  # For admin routes

    register_blueprints(app)        # Register other blueprints

    return app

def register_blueprints(app):
    from app.routes.user_routes import user_bp
    from app.routes.public_routes import public_bp

    app.register_blueprint(user_bp)    # Register user routes
    app.register_blueprint(public_bp)  # Register public routes
