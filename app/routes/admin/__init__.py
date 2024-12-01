# app/routes/admin/__init__.py
from flask import Blueprint

# Define the admin blueprint with url_prefix='/admin'
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# No need to register child blueprints here since they are registered in app/__init__.py
