from flask import Flask
from .extensions import db, migrate
from .models import *
from config import get_config

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    print(f"Selected configuration name: {config_name}")
    
    app = Flask(__name__)
    config_class = get_config(config_name)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    from .routes import admin_routes, public_bot_routes, public_user_routes
    app.register_blueprint(admin_routes.bp)  # Ensure 'bp' is correctly imported

    return app

print(f"App module loaded")
