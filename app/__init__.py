import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config_by_name

db = SQLAlchemy()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    
    # Ensure the instance directory exists
    os.makedirs(app.instance_path, exist_ok=True)
    
    init_extensions(app)
    init_routes(app)
    
    return app

def init_extensions(app):
    db.init_app(app)

def init_routes(app):
    from app.routes.admin import admin_bp
    from app.routes.user import user_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp, url_prefix='/user')
