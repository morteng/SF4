from flask import Blueprint

user_bp = Blueprint('admin_user', __name__)

# Define your routes here, for example:
@user_bp.route('/users', methods=['GET'])
@login_required
def list_users():
    from app.services.user_service import list_all_users
    users = list_all_users()
    return render_template('admin/user_list.html', users=users)

@user_bp.route('/greet')
def greet():
    return "Hey there, buddy!"
