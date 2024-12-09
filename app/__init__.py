from flask import Flask
from app.routes.admin import register_admin_blueprints

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # ... other configurations ...
    
    from .routes import register_blueprints
    register_blueprints(app)
    
    return app

# In your routes/__init__.py
from .admin import register_admin_blueprints

def register_blueprints(app):
    register_admin_blueprints(app)
