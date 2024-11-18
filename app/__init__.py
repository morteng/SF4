from flask import Flask
from .extensions import init_extensions, login_manager
from .models.user import User

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Load configuration
    from .config import get_config
    config = get_config(config_name)
    if config:
        app.config.from_object(config)
    else:
        raise ValueError(f"Unknown configuration name: {config_name}")

    # Initialize extensions
    init_extensions(app)

    # User loader callback for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from .routes import register_blueprints
    register_blueprints(app)

    return app
