from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import get_config

db = SQLAlchemy()

def create_app(config_name):
    app = Flask(__name__)
    config = get_config(config_name)
    app.config.from_object(config)

    db.init_app(app)

    with app.app_context():
        from .routes import register_routes
        register_routes(app)

    return app
