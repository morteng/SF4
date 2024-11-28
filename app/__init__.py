from flask import Flask
from .config import config_by_name
from .extensions import db, login_manager

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    
    db.init_app(app)
    login_manager.init_app(app)
    
    # Assuming there is a blueprint defined in routes.py
    from .routes import blueprint
    app.register_blueprint(blueprint)
    
    return app
