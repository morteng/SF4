from flask import Blueprint

public_routes = Blueprint('public', __name__)

@public_routes.route('/')
def index():
    return "Welcome to the Stipend Discovery Website!"
