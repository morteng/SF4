from flask import Flask
from .config import config_by_name
from .extensions import db, login_manager
from .models import init_models  # Import the function
from .models.user import User  # Import the User model
from .routes.api import api_bp  # Import the API blueprint
from .routes.admin.auth_routes import auth_bp  # Import the admin auth blueprint
from .routes.admin.__init__ import register_admin_blueprints  # Import the registration function
from flask_migrate import Migrate  # Import Migrate

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate = Migrate(app, db)  # Initialize Flask-Migrate

    # Set up user loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Initialize models
    with app.app_context():
        init_models(app)

    # Register blueprints
    from .routes.admin.bot_routes import admin_bot_bp
    from .routes.admin.organization_routes import org_bp as admin_org_bp
    from .routes.admin.stipend_routes import admin_stipend_bp
    from .routes.admin.tag_routes import tag_bp as admin_tag_bp
    from .routes.admin.user_routes import user_bp as admin_user_bp
    from .routes.user_routes import user_bp
    from .routes.visitor_routes import visitor_bp

    app.register_blueprint(api_bp)  # Register the API blueprint
    app.register_blueprint(auth_bp)  # Register the admin auth blueprint
    register_admin_blueprints(app)  # Register all admin blueprints

    return app
