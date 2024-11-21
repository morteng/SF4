import os
from flask import Flask
from config import Config
from app.extensions import init_extensions, init_admin_user

def create_app(config_name='default'):
    # Initialize the Flask application
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    # Ensure the instance/ directory exists
    instance_path = app.instance_path
    if not os.path.exists(instance_path):
        print(f"Creating directory: {instance_path}")  # Debugging line
        os.makedirs(instance_path)

    # Initialize extensions and routes
    init_extensions(app)
    init_routes(app)
    init_admin_user(app)

    return app

def init_routes(app):
    from app.routes.admin import admin_bp
    from app.routes.user import user_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp, url_prefix='/user')

# Other initialization functions can be added here
