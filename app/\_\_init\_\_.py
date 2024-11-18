from flask import Flask
from .config import get_config  # Use get_config function instead of importing Config directly
from app.extensions import db

def create_app(config_name='default'):
    # Create and configure the app
    app = Flask(__name__)
    
    # Load configuration based on environment variable or default to 'default'
    config_class = get_config(config_name)
    app.config.from_object(config_class)

    # Print the configuration class being used
    print(f"Loaded configuration: {config_class.__name__}")

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    from app.routes.admin import admin_bp
    from app.routes.user import user_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp, url_prefix='/user')

    return app

# Ensure the database is created when the application starts
def init_db(app):
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    config_name = os.getenv('FLASK_CONFIG', 'default')
    app = create_app(config_name)
    init_db(app)
    app.run()
