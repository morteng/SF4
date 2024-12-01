from flask import Flask
from app.extensions import db
from app.config import config_by_name

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    db.init_app(app)
    return app
