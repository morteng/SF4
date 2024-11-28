from flask import Flask
from .config import config_by_name
from .extensions import db, login_manager
from .models import init_models  # Import the function
from .models.user import User  # Import the User model

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Set up user loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Initialize models
    with app.app_context():
        init_models(app)

    # Register blueprints
    from .routes import routes_bp  # Changed here
    app.register_blueprint(routes_bp)  # And here

    return app
