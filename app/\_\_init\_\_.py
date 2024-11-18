from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import get_config

db = SQLAlchemy()

def create_app(config_name='default'):
    app = Flask(__name__)
    config = get_config(config_name)
    app.config.from_object(config)

    db.init_app(app)

    # Register blueprints, etc.
    from app.routes import register_routes
    register_routes(app)

    return app

# Initialize the database
def init_db(app):
    with app.app_context():
        db.create_all()
