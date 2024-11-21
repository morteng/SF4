from flask import Blueprint

# Import individual user route modules
from .user_routes import user_bp

# No need to register blueprints here, they will be registered in the main routes/__init__.py
