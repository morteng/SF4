from flask import Blueprint

public_user_bp = Blueprint('public_user', __name__)

# Import routes to register them
from . import user_routes  # Assuming there are other routes in this file or submodules

print("Public user blueprint initialized successfully.")
