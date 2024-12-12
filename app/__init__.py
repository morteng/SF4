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
        app.config['SECRET_KEY'] = 'test_secret_key'  # Add this line
        app.config['TEMPLATES_AUTO_RELOAD'] = True  # Enable template auto-reload for testing
    else:
        from app.config import config_by_name
        app.config.from_object(config_by_name[config_name])

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    from app.models.user import User  # Import the User model

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))  

    # Register blueprints
    from app.routes.admin import register_admin_blueprints
    register_admin_blueprints(app)  # For admin routes

    from app.routes import register_blueprints
    register_blueprints(app)        # Register other blueprints

    return app
