from flask import Flask
from .routes import init_routes
from .extensions import db, init_extensions

def create_app(config_name='default'):
    from .config import get_config
    config = get_config(config_name)
    
    app = Flask(__name__)
    app.config.from_object(config)

    # Initialize extensions
    init_extensions(app)

    # Initialize routes
    init_routes(app)

    return app
