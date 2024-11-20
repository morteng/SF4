from flask import Blueprint, render_template

visitor_bp = Blueprint('visitor', __name__)

@visitor_bp.route('/', methods=['GET'])
def index():
    # Logic for visitor home page
    return render_template('index.html')

@visitor_bp.route('/about', methods=['GET'])
def about():
    # Logic for about page
    return render_template('about.html')
