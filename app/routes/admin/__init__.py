from flask import Blueprint

admin_bp = Blueprint('admin', __name__)

# Import routes to register them
from .auth_routes import *  # Added this line
from .bot_routes import *
from .organization_routes import *
from .stipend_routes import *
from .tag_routes import *
from .user_routes import *

print("Admin blueprint initialized successfully.")
