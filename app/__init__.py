from flask import Flask
from flask_migrate import Migrate
from .config import config_by_name
from .extensions import db, login_manager
from .models import init_models
from .models.user import User
from .routes.admin.__init__ import register_admin_blueprints
from .routes.user_routes import user_bp
from .routes.public_routes import public_bp
import os

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate = Migrate(app, db)

    # Set up user loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Ensure the database is initialized and the admin user is set up
    with app.app_context():
        init_models(app)  # Pass the app instance here
        from app.utils import init_admin_user
        init_admin_user()

    # Register blueprints
    register_admin_blueprints(app)
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(public_bp)

    return app
