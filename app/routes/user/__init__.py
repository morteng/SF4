from flask import Blueprint
from app.utils import admin_required  # Ensure this is the correct function

user_bp = Blueprint('user', __name__)

# Example of using admin_required, adjust as necessary
# @user_bp.route('/some_route')
# @admin_required
# def some_view():
#     pass

from .user_routes import *
