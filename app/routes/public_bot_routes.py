from flask import Blueprint, render_template

public_bot_bp = Blueprint('public_bot', __name__, url_prefix='/bots')

@public_bot_bp.route('/')
def index():
    return render_template('bots/index.html', title='Bot Information')
