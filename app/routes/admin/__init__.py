from flask import Blueprint

admin_bp = Blueprint('admin', __name__)

from .bot_routes import *
from .organization_routes import *
from .stipend_routes import *
from .tag_routes import *
# from .user_routes import *  # Commented out or removed
