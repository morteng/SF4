from flask import Flask
from app.extensions import db
from app.routes import register_blueprints

def create_app(config_name='default'):
    from config import get_config
    config = get_config(config_name)
    
    app = Flask(__name__)
    app.config.from_object(config)

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    with app.app_context():
        register_blueprints(app)

    return app
