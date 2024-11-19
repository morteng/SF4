from flask import Flask
from app.config import get_config
from app.extensions import init_extensions
from app.routes import init_routes as init_app_routes

def create_app(config_name='default'):
    # Load configuration
    config = get_config(config_name)
    app = Flask(__name__)
    app.config.from_object(config)

    # Initialize extensions
    init_extensions(app)

    # Initialize routes
    init_app_routes(app)

    return app
