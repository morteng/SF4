from flask import Blueprint, request, jsonify, session
from app.utils import login_required
from app.services.user_service import create_user, get_user_by_username, authenticate_user

user_bp = Blueprint('user', __name__, url_prefix='/users')

@user_bp.route('/index', methods=['GET'])
@login_required
def index():
    return render_template('user/index.html')
