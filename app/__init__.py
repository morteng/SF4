from flask import Flask
from .extensions import init_extensions
from .models import init_models
from .routes import init_routes

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Load configuration
    from .config import get_config
    config = get_config(config_name)
    app.config.from_object(config)

    # Initialize extensions
    init_extensions(app)

    # Initialize models
    init_models(app)

    # Initialize routes
    init_routes(app)

    return app
