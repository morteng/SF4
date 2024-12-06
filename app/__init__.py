from flask import Flask
from flask_migrate import Migrate
from .config import config_by_name
from .extensions import db, login_manager
from .models import init_models
from .models.user import User
from .routes.api import api_bp
from .routes.admin.auth_routes import auth_bp
from .routes.admin.__init__ import register_admin_blueprints
from .routes.user_routes import user_bp
from .routes.visitor_routes import visitor_bp

# AI ensure db file is created if it does not already exist, and make sure tables are created and default admin user is added. read all the impåortant values from .env file (it's there even if you cannot see it). AI!

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

    # Initialize models
    with app.app_context():
        init_models(app)

    # Register blueprints
    app.register_blueprint(api_bp)
    app.register_blueprint(auth_bp)
    register_admin_blueprints(app)  # This function handles all admin-related blueprints
    app.register_blueprint(user_bp)
    app.register_blueprint(visitor_bp)

    return app
