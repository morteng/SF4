import os
from flask import Flask, current_app
from app.config import get_config
from app.extensions import init_extensions
from app.routes.admin import admin_bp
from app.routes.user import user_bp

def create_app(config_name='default'):
    # Create and configure the app
    app = Flask(__name__)
    config = get_config(config_name)
    app.config.from_object(config)

    # Initialize extensions
    init_extensions(app)

    # Register blueprints
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp, url_prefix='/user')

    return app

if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_CONFIG', 'development'))
    with app.app_context():
        print("Admin blueprint initialized successfully.")
        # Run the application
        app.run()
