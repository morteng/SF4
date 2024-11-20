from flask import Blueprint, render_template

# Create a blueprint for public routes
public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def index():
    return render_template('index.html')
