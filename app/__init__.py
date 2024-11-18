from .config import get_config  # Use get_config function instead of importing Config directly
from flask import Flask
from dotenv import load_dotenv

def create_app(config_name=None):
    load_dotenv()
    
    app = Flask(__name__)
    config = get_config(config_name or os.getenv('FLASK_CONFIG', 'default'))
    app.config.from_object(config)
    
    # Initialize extensions and blueprints here
    
    return app
