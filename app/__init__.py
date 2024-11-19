from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from .routes import init_routes

# Initialize migrate and login manager objects
migrate = Migrate()
login_manager = LoginManager()

def create_app(config_name='default'):
    app = Flask(__name__)

    # Load configuration
    from .config import get_config
    config = get_config(config_name)
    app.config.from_object(config)

    # Initialize the database object
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy()
    db.init_app(app)

    # Initialize migrate and login manager
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # User loader callback for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from .models.user import User
        return User.query.get(int(user_id))

    # Initialize models
    from .models import init_models
    init_models(app)

    # Initialize routes
    init_routes(app)

    return app
