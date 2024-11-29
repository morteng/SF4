from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Import specific route modules here
from . import bot_api
