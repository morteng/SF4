import os
from flask import Flask
from config import Config
from app.extensions import init_extensions, init_admin_user, db, migrate

def create_app(config_name='default'):
    # Initialize the Flask application
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    # Print the current working directory for debugging
    print(f"Current Working Directory: {os.getcwd()}")  # Debugging line

    # Ensure the instance/ directory exists
    instance_path = app.instance_path
    if not os.path.exists(instance_path):
        print(f"Creating directory: {instance_path}")  # Debugging line
        os.makedirs(instance_path)
    else:
        print(f"Directory already exists: {instance_path}")  # Debugging line

    # Print the database URI for debugging
    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")  # Debugging line

    # Initialize extensions and routes
    init_extensions(app)
    init_routes(app)

    return app

def init_routes(app):
    from app.routes.admin import admin_bp
    from app.routes.user import user_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp, url_prefix='/user')

# Other initialization functions can be added here
