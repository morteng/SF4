from flask import Blueprint

# Create a blueprint for user routes
user_bp = Blueprint('user', __name__, url_prefix='/user')

# Import routes to register them with the blueprint
from .user_routes import *
