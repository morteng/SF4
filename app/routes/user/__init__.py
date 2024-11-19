from flask import Blueprint, request, jsonify, session
from app.utils import login_required
from app.services.user_service import create_user, get_user_by_username, authenticate_user

user_bp = Blueprint('user', __name__, url_prefix='/users')

@user_bp.route('/profile/<int:user_id>', methods=['GET'])
@login_required
def profile(user_id):
    from app.services.user_service import get_user_by_id
    user = get_user_by_id(user_id)
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('user.index'))
    return render_template('user/profile.html', user=user)
