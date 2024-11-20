from flask import Blueprint, render_template

visitor_bp = Blueprint('visitor', __name__)

@visitor_bp.route('/')
def index():
    # Logic for visitor home page
    return render_template('index.html')

@visitor_bp.route('/about')
def about():
    # Logic for about page
    return render_template('about.html')
