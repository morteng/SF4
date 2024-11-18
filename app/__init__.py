from dotenv import load_dotenv
import os
from .config import get_config  # Use get_config function instead of importing Config directly
from flask import Flask

def create_app(config_name=None):
    load_dotenv()
    
    print("Environment variables:", dict(os.environ))  # Add this line to verify .env loading
    
    app = Flask(__name__)
    config = get_config(config_name or os.getenv('FLASK_CONFIG', 'default'))
    app.config.from_object(config)
    
    # Initialize extensions and blueprints here
    from .extensions import db
    db.init_app(app)

    from .routes.public_user_routes import public_user_bp
    from .routes.public_bot_routes import public_bot_bp
    app.register_blueprint(public_user_bp)
    app.register_blueprint(public_bot_bp)

    return app
