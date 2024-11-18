from flask import Blueprint, render_template

bp = Blueprint('public_bots', __name__, url_prefix='/bots')

@bp.route('/')
def public_bots():
    return render_template('public/bots.html')
