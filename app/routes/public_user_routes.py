from flask import Blueprint, render_template

bp = Blueprint('public_users', __name__, url_prefix='/users')

@bp.route('/')
def public_users():
    return render_template('public/users.html')
