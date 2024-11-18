from flask import Flask
from app.config import get_config
from app.extensions import db, migrate

def create_app(config_name):
    app = Flask(__name__)
    config = get_config(config_name)
    app.config.from_object(config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes import register_routes
    register_routes(app)

    return app
