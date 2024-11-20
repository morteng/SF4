from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# Initialize extensions here
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'public.index'

    from .routes.public_routes import public_bp
    from .routes.user_routes import user_bp  # Import the user blueprint

    app.register_blueprint(public_bp)  # Register the public routes
    app.register_blueprint(user_bp, url_prefix='/user')  # Register the user routes with a prefix

    init_extensions(app)
    init_models(app)

    return app

def init_extensions(app):
    from .extensions import init_extensions as _init_extensions
    _init_extensions(app)

def init_models(app):
    from .models import init_models as _init_models
    _init_models(app)
