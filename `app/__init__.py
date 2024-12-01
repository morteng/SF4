from flask import Flask
from app.config import config_by_name
from app.extensions import init_extensions

def create_app(config_name, instance_path=None):
    app = Flask(__name__, instance_path=instance_path)
    app.config.from_object(config_by_name[config_name])
    init_extensions(app)
    # Register blueprints and other initializations
    return app
