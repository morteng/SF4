from flask import Flask
from .config import get_config  # Use relative import
from .extensions import init_extensions  # Use relative import
import routes

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(get_config(config_name))

    init_extensions(app)

    # Initialize admin routes
    routes.init_routes(app)

    return app
